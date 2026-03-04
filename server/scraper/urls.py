from django.urls import path
from . import views

urlpatterns = [
    path("", views.search_page, name="search"),
    path("history/", views.history_page, name="history"),
    path("searches/<int:search_id>/", views.search_detail, name="search_detail"),
]
