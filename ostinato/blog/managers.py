from django.db import models


class BlogEntryManager(models.Manager):

    def published(self):
        return self.get_query_set().filter(state=5)

