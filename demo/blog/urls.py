from django.conf.urls import url
from django.conf import settings

from blog.models import Entry
from blog.views import EntryPreviewView, EntryDetailView


urlpatterns = [
    url(r'^(?P<id>[\d]+)/$', EntryPreviewView.as_view(), name="blog_entry_preview"),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        EntryDetailView.as_view(), name="blog_entry_detail"),
]

