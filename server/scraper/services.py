from django.conf import settings
from django.core.files.base import ContentFile
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .models import Search, ImageAsset


"""
Extract all image URLs from HTML content and resolve relative URLs.

Args:
    page_url (str): The base URL of the page for resolving relative image URLs.
    html (str): The HTML content to parse for image tags.

Returns:
    list[str]: A list of unique, absolute image URLs found in the HTML.

Description:
    Parses HTML using BeautifulSoup, extracts all img tag src attributes,
    resolves relative URLs to absolute URLs, and removes duplicates.
"""
def extract_image_urls(page_url: str, html: str) -> list[str]:
    # love this library!
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []

    # scrape all img tags and extract src
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        urls.append(urljoin(page_url, str(src)))

    # remove duplicate image urls
    capturedUrls = set()
    out = []
    for u in urls:
        if u not in capturedUrls:
            capturedUrls.add(u)
            out.append(u)

    # out = list(set(urls))
    return out

"""
Map a MIME content type to a safe file extension.

Args:
    content_type (str | None): The MIME content type string (e.g., "image/jpeg").

Returns:
    str: A file extension string including the leading dot (e.g., ".jpg").
         Returns ".bin" if content_type is None, or ".img" for unmapped types.

Description:
    Normalizes and parses the content type header, extracting the primary type,
    and returns the appropriate file extension. Handles edge cases like parameters
    in content type headers (e.g., "image/jpeg; charset=utf-8").
"""
def create_safe_extension(content_type: str | None) -> str:
    if not content_type:
        return ".bin"
    ct = content_type.lower().split(";")[0].strip()
    print(f"\n\nDetermining file extension for content type: {ct}\n\n")
    return {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
        "image/avif": ".avif",
    }.get(ct, ".img")

"""
Perform a web scrape operation to extract and save images from a given URL.

Args:
    url (str): The URL of the webpage to scrape for images.

Returns:
    Search: A Search model instance containing metadata about the scraping operation.

Description:
    Creates a Search record, fetches the webpage content, extracts image URLs,
    downloads each image with appropriate headers and timeout, validates content type,
    and saves ImageAsset records with the downloaded files. Silently skips failed
    image downloads and non-image content types.

Raises:
    requests.exceptions.RequestException: If the initial page request fails.
"""
def run_search(url: str) -> Search:

    # create the Search record first so we have an ID to associate with the ImageAssets
    search = Search.objects.create(url=url)

    headers = {"User-Agent": settings.USER_AGENT}
    timeout = settings.REQUEST_TIMEOUT_SECONDS

    resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()

    image_urls = extract_image_urls(url, resp.text)[: settings.MAX_IMAGES]
    print(f"Extracted {len(image_urls)} image URLs: {image_urls}")

    # loop through the image URLs and create ImageAsset records
    for index, img_url in enumerate(image_urls, start=1):
        try:
            r = requests.get(
                img_url, headers=headers, timeout=timeout, allow_redirects=True
            )
            r.raise_for_status()
            content_type = r.headers.get("Content-Type")

            # only save if the content type indicates it's an image
            if not (content_type or "").lower().startswith("image/"):
                continue

            safe_extension = create_safe_extension(content_type)
            filename = f"search_{search.id}_img_{index}{safe_extension}"

            # create the ImageAsset record and save the file
            asset = ImageAsset(
                search=search, source_url=img_url, content_type=content_type or ""
            )
            asset.file.save(filename, ContentFile(r.content), save=True)

        except Exception:
            continue

    return search
