from django.db import models
from django.urls import reverse

from ostinato.blog.models import BlogEntryBase
from taggit.managers import TaggableManager
from website.models import SEOPage


class Entry(BlogEntryBase):
    tags = TaggableManager()

    class Meta:
        verbose_name_plural = "Entries"

    def get_absolute_url(self):
        if self.publish_date:
            return reverse("blog_entry_detail", kwargs={
                'year': self.publish_date.year,
                'month': self.publish_date.strftime('%m'),
                'day': self.publish_date.strftime('%d'),
                'slug': self.slug,
            })
        else:
            return reverse("blog_entry_preview", args=[self.id])


class LandingPage(SEOPage):
    max_latest_entries = models.IntegerField(
        default=10,
        help_text="The maximum number of latest entries to display")
