from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


class PageManager(models.Manager):

    def published(self):
        return self.get_query_set().filter(
            publish_date__lte=timezone.now(), state=5)

    def get_navbar(self, for_page=None):
        """
        Returns a dictionary of pages with their short titles and urls.

        ``for_page`` is an instance of Page. If specified, will only
        return immediate child pages for that page.
        """
        to_return = []

        if for_page == '':
            for_page = None

        nav_items = self.published().filter(parent=for_page, show_in_nav=True)\
            .order_by('tree_id')

        if nav_items:
            for page in nav_items:
                to_return.append({
                    'slug': page.slug,
                    'title': page.get_short_title(),
                    'url': page.get_absolute_url(),
                })

        return to_return

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
        """
        Cycle through every slug in the path to try and find the current
        page.

        Returns a tuple containing the Page and any sub-urlpath that might
        precede the page slug.

        TODO: More descriptive doctype pls

        TODO: We should probably look for the page based on more than just
        the slug, since a sub-url might exist with the same "slug" as a page.
        A possible solution would be to match the page with the parent (if any)

        This leads me to believe we should be caching/indexing page urls
        somewhere for a quick lookup.
        """

        page = None
        path = url_path.split('/')
        sub_path = []

        while not page:
            try:
                page = self.get_query_set().get(slug=path[-1])

            except ObjectDoesNotExist:
                if path:
                    # Save the failed slug so we can return it later
                    sub_path.insert(0, path[-1])
                    path = path[:-1]  # Remove the failed slug

                if not path: break

        if sub_path:
            sub_path = '/' + '/'.join(sub_path)
        else:
            sub_path = None

        if sub_path == '/':
            sub_path = None

        return page, sub_path

