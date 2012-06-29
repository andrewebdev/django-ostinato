from django.db import models

from ostinato.blog.models import BlogEntryBase


class Entry(BlogEntryBase):

    class Meta:
        verbose_name_plural = 'Entries'
