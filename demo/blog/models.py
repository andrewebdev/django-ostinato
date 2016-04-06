from django.db import models

from ostinato.blog.models import BlogEntryBase
from ostinato.pages.registry import page_content
from taggit.managers import TaggableManager
from website.models import SEOPage


class Entry(BlogEntryBase):
    tags = TaggableManager()

    class Meta:
        verbose_name_plural = "Entries"

    @models.permalink
    def get_absolute_url(self):
        if self.publish_date:
            return ("blog_entry_detail", [], {
                'year': self.publish_date.year,
                'month': self.publish_date.strftime('%m'),
                'day': self.publish_date.strftime('%d'),
                'slug': self.slug,
            })
        else:
            return ("blog_entry_preview", [self.id], {})


@page_content.register
class LandingPage(SEOPage):
    max_latest_entries = models.IntegerField(default=10,
        help_text="The maximum number of latest entries to display")

    class ContentOptions:
        template = 'blog/landing_page.html'
        view = 'blog.views.LandingPageView'