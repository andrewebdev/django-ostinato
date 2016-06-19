from django.db import models
from django.utils import timezone


class BlogEntryManager(models.Manager):

    def published(self):
        return self.get_queryset().filter(state='published',
                                          publish_date__lte=timezone.now())

