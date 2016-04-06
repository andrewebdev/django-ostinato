from django.db import models


class BlogEntryManager(models.Manager):

    def published(self):
        return self.get_queryset().filter(state=5)

