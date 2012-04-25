from django.db import models
from django.utils import timezone


class PageManager(models.Manager):

    def published(self):
        return self.get_query_set().filter(
            publish_date__lte=timezone.now(), _sm__state='published').distinct()

    def get_navbar(self, for_page=None):
        """
        Returns a dictionary of pages with their short titles and urls.

        ``for_page`` is an instance of Page. If specified, will only
        return immediate child pages for that page.
        """
        to_return = []
        nav_items = self.published().filter(parent=for_page, show_in_nav=True)

        if nav_items:
            for item in nav_items:
                to_return.append({
                    'title': item.get_short_title(),
                    'url': item.get_absolute_url(),
                })

        return to_return

