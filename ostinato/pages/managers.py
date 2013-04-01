from django.db import models
from django.core.cache import get_cache
from django.utils import timezone

from mptt.managers import TreeManager


class PageManager(TreeManager):

    def published(self):
        return self.get_query_set().filter(
            publish_date__lte=timezone.now(), state=5)

    def get_navbar(self, for_page=None, clear_cache=False):
        """
        Returns a dictionary of pages with their short titles and urls.

        ``for_page`` is an instance of Page. If specified, will only
        return immediate child pages for that page.
        """
        cache = get_cache('default')
        if for_page:
            cache_key = 'ostinato:pages:page:%s:navbar' % for_page.id
        else:
            cache_key = 'ostinato:pages:page:root:navbar'

        if clear_cache:
            cache.delete(cache_key)

        # Try to get the path from the cache
        navbar = cache.get(cache_key)

        if not navbar:
            navbar = []
            nav_items = self.published().filter(parent=for_page, show_in_nav=True)
            for page in nav_items:
                navbar.append({
                    'slug': page.slug,
                    'title': page.get_short_title(),
                    'url': page.get_absolute_url(),
                })

            # Set the cache to timeout after a month
            cache.set(cache_key, navbar, 60 * 60 * 24 * 7 * 4)

        return navbar

    def get_breadcrumbs(self, for_page, clear_cache=False):
        """
        Returns a list of all the parents, plus the current page. Each item
        in the list contains a short title and url.
        """
        cache = get_cache('default')
        cache_key = 'ostinato:pages:page:%s:crumbs' % for_page.id

        if clear_cache:
            cache.delete(cache_key)

        crumbs = cache.get(cache_key)

        if not crumbs:
            parents = for_page.get_ancestors()
            crumbs = []
            for page in parents:
                crumbs.append({
                    'slug': page.slug,
                    'title': page.get_short_title(),
                    'url': page.get_absolute_url(),
                })
            crumbs.append({
                'slug': for_page.slug,
                'title': for_page.get_short_title(),
                'url': for_page.get_absolute_url()
            })

            # Set the cache to timeout after a month
            cache.set(cache_key, crumbs, 60 * 60 * 24 * 7 * 4)

        return crumbs

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

    def generate_url_cache(self):
        cache = get_cache('default')
        for page in self.get_query_set().all():
            page.get_absolute_url()

    def clear_url_cache(self):
        cache = get_cache('default')
        page_ids = list(self.get_query_set().values_list('id', flat=True))
        cache.delete_many(['ostinato:pages:page:%s:url' % i for i in page_ids])

    def clear_navbar_cache(self):
        cache = get_cache('default')
        page_ids = list(self.get_query_set().values_list('id', flat=True))
        cache.delete('ostinato:pages:page:root:navbar')
        cache.delete_many(
            ['ostinato:pages:page:%s:navbar' % i for i in page_ids])

    def clear_breadcrumbs_cache(self):
        cache = get_cache('default')
        page_ids = list(self.get_query_set().values_list('id', flat=True))
        cache.delete_many(
            ['ostinato:pages:page:%s:crumbs' % i for i in page_ids])
