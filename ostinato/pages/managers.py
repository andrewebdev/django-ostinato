from django.db import models
from django.utils import timezone

from mptt.managers import TreeManager


class PageManager(TreeManager):

    def published(self):
        return self.get_query_set().filter(
            publish_date__lte=timezone.now(), state=5)

    def get_navbar(self, for_page=None):
        """
        Returns a dictionary of pages with their short titles and urls.

        ``for_page`` is an instance of Page. If specified, will only
        return immediate child pages for that page.
        """
        navbar = []

        nav_items = self.published().filter(parent=for_page, show_in_nav=True)

        if nav_items:
            for page in nav_items:
                navbar.append({
                    'slug': page.slug,
                    'title': page.get_short_title(),
                    'url': page.get_absolute_url(),
                })

        return navbar

    def get_breadcrumbs(self, for_page):
        """
        Returns a list of all the parents, plus the current page. Each item
        in the list contains a short title and url.
        """
        to_return = []
        parents = for_page.get_ancestors()

        if parents:
            for page in parents:
                to_return.append({
                    'slug': page.slug,
                    'title': page.get_short_title(),
                    'url': page.get_absolute_url(),
                })

        to_return.append({
            'slug': for_page.slug,
            'title': for_page.get_short_title(),
            'url': for_page.get_absolute_url()
        })

        return to_return

    def get_from_path(self, url_path):
        """ Returns a page object, base on the url path. """

        path = url_path.split('/')
        path.reverse()

        ## TODO: Maybe we should cache the page paths somewhere, so that
        ## we dont have to do a query for each page.
        for node in path:
            try:
                if node:
                    page = self.get_query_set().get(slug=node)
                    return page
            except:
                pass


