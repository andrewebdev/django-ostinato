from django.db import models

from ostinato.blog.models import BlogEntryBase
from ostinato.pages.registry import page_content
from taggit.managers import TaggableManager
from website.models import SEOPage


class Entry(BlogEntryBase):
    tags = TaggableManager()

    class Meta:
        verbose_name_plural = "Entries"


@page_content.register
class LandingPage(SEOPage):
    max_latest_entries = models.IntegerField(default=10,
        help_text="The maximum number of latest entries to display")

    class ContentOptions:
        template = 'blog/landing_page.html'
        view = 'blog.views.LandingPageView'