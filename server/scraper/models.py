from django.db import models

class Search(models.Model):
    url = models.URLField(max_length=2048, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.id} {self.url}"
    
    
class ImageAsset(models.Model):
    search = models.ForeignKey(Search, on_delete=models.CASCADE, related_name="images")
    source_url = models.URLField(max_length=4096)
    file = models.FileField(upload_to="searches/%Y/%m/%d/")
    content_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["search", "source_url"], name="uq_search_source_url")
        ]

    def __str__(self) -> str:
        return f"{self.search_id} {self.source_url}"
