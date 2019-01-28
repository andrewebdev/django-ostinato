from django.urls import path
from blog.views import EntryPreviewView, EntryDetailView


urlpatterns = [
    path('<int:id>/', EntryPreviewView.as_view(), name="blog_entry_preview"),

    path(
        '<int:year>/<int:month>/<int:day>/<slug:slug>/',
        EntryDetailView.as_view(),
        name="blog_entry_detail"
    ),
]
