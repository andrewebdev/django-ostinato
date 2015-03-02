from django.core.cache import get_cache
from django.utils import timezone
from django.conf import settings

from mptt.managers import TreeManager
from ostinato.pages import PAGES_SETTINGS


class PageManager(TreeManager):

    def published(self):
        return self.get_queryset().filter(
            publish_date__lte=timezone.now(), state=5)

    def get_navbar(self, for_page=None, clear_cache=False):
        """
        Returns a dictionary of pages with their short titles and urls.

        ``for_page`` is an instance of Page. If specified, will only
        return immediate child pages for that page.
        """
        PAGES_SITE_TREEID = getattr(settings, 'OSTINATO_PAGES_SITE_TREEID', None)

        cache = get_cache(PAGES_SETTINGS['CACHE_NAME'])
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

            if PAGES_SITE_TREEID:
                nav_items = self.published().filter(
                    parent__level=0, parent__tree_id=PAGES_SITE_TREEID,
                    show_in_nav=True)

            else:
                nav_items = self.published().filter(
                    parent=for_page, show_in_nav=True)

            for page in nav_items:
                navbar.append({
                    'slug': page.slug,
                    'title': page.get_short_title(),
                    'url': page.get_absolute_url(),
                    'tree_id': page.tree_id,
                    'level': page.level,
                })

            # Set the cache to timeout after a month
            cache.set(cache_key, navbar, 60 * 60 * 24 * 7 * 4)

        return navbar

    def get_breadcrumbs(self, for_page, clear_cache=False):
        """
        Returns a list of all the parents, plus the current page. Each item
        in the list contains a short title and url.
        """
        cache = get_cache(PAGES_SETTINGS['CACHE_NAME'])
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

    def get_from_path(self, url_path, clear_cache=False):
        """ Returns a page object, base on the url path. """
        cache = get_cache(PAGES_SETTINGS['CACHE_NAME'])
        cache_key = 'ostinato:pages:page_for_path:%s' % url_path

        if clear_cache:
            cache.delete(cache_key)

        page = cache.get(cache_key)

        if not page:
            path = url_path.split('/')
            path.reverse()

            for node in path:
                try:
                    if node:
                        page = self.get_queryset().get(slug=node)
                        cache.set(cache_key, page, 60 * 60 * 24 * 7 * 4)
                        break
                except:
                    pass

        return page

    def generate_url_cache(self):
        for page in self.get_queryset().all():
            page.get_absolute_url()

    def clear_url_cache(self):
        cache = get_cache(PAGES_SETTINGS['CACHE_NAME'])
        pages = self.get_queryset()
        page_ids = list(pages.values_list('id', flat=True))
        # We must clear the page_for_path cache before the normal url cache
        # since get_absolute_url() will create a cache if it doesn't exist
        cache.delete_many(['ostinato:pages:page_for_path:%s' % p.get_absolute_url() for p in pages])
        cache.delete_many(['ostinato:pages:page:%s:url' % i for i in page_ids])

    def clear_navbar_cache(self):
        cache = get_cache(PAGES_SETTINGS['CACHE_NAME'])
        page_ids = list(self.get_queryset().values_list('id', flat=True))
        cache.delete('ostinato:pages:page:root:navbar')
        cache.delete_many(
            ['ostinato:pages:page:%s:navbar' % i for i in page_ids])

    def clear_breadcrumbs_cache(self):
        cache = get_cache(PAGES_SETTINGS['CACHE_NAME'])
        page_ids = list(self.get_query_set().values_list('id', flat=True))
        cache.delete_many(
            ['ostinato:pages:page:%s:crumbs' % i for i in page_ids])
