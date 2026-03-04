from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count

from .models import Search
from .forms import SearchForm
from .services import run_search

"""
Handle search form submission and rendering.

Args:
    request (HttpRequest): The HTTP request object.
    
Returns:
    HttpResponse: Rendered search form page or redirect to search detail.
    
Methods:
    POST: Validates and processes search form submission.
           - Takes URL from form data
           - Executes search via run_search service
           - Redirects to search detail page on success
           - Shows error message if search fails
    GET: Renders empty search form
    
Raises:
    Exception: Caught and displayed as error message to user.
"""
def search_page(request):
    # Handle form submission
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]
            try:
                search = run_search(url)
                return redirect("search_detail", search_id=search.id)
            except Exception as e:
                messages.error(request, f"Failed to fetch URL: {e}")
    else:
        # GET request, render the form
        form = SearchForm()

    return render(request, "scraper/search.html", {"form": form})

"""
Display details of a specific search result.

Args:
    request (HttpRequest): The HTTP request object.
    search_id (int): The ID of the search to display.
    
Returns:
    HttpResponse: Rendered search detail page with search object and images.
    
Raises:
    Http404: If search with given ID does not exist.
    
Notes:
    - Uses prefetch_related optimization for images queryset
    - Displays info message showing number of images found
"""
def search_detail(request, search_id: int):
    search = get_object_or_404(Search.objects.prefetch_related("images"), id=search_id)
    return render(request, "scraper/detail.html", {"search": search})

"""
Display paginated history of all searches.

Args:
    request (HttpRequest): The HTTP request object.
    
Returns:
    HttpResponse: Rendered history page with list of searches.
    
Context:
    searches (QuerySet): List of up to 200 most recent searches,
                        annotated with image count and ordered by creation date.
"""
def history_page(request):
    searches = Search.objects.annotate(image_count=Count("images")).order_by("-created_at")[:200]
    return render(request, "scraper/history.html", {"searches": searches})