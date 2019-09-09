from django.core.cache import caches
from django.utils import timezone

from mptt.managers import TreeManager
from ostinato.pages import PAGES_SETTINGS, get_cache_key


class PageManager(TreeManager):

    def published(self):
        return self.get_queryset().filter(state='public')

    def get_breadcrumbs(self, for_page, clear_cache=False):
        """
        Returns a list of all the parents, plus the current page. Each item
        in the list contains a short title and url.
        """
        cache = caches[PAGES_SETTINGS['cache_name']]
        cache_key = 'ostinato:pages:page:{0}:crumbs'.format(for_page.id)

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
        cache = caches[PAGES_SETTINGS['cache_name']]
        cache_key = 'ostinato|pages|page_for_path|{0}'.format(url_path)

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
        cache = caches[PAGES_SETTINGS['cache_name']]
        pages = self.get_queryset()
        page_ids = list(pages.values_list('id', flat=True))
        # We must clear the page_for_path cache before the normal url cache
        # since get_absolute_url() will create a cache if it doesn't exist
        cache.delete_many([
            get_cache_key('page_for_path', p.get_absolute_url())
            for p in pages
        ])
        cache.delete_many([
            get_cache_key('page', str(i), 'url')
            for i in page_ids
        ])

    def clear_breadcrumbs_cache(self):
        cache = caches[PAGES_SETTINGS['cache_name']]
        page_ids = list(self.get_queryset().values_list('id', flat=True))
        cache.delete_many([
            get_cache_key('page', str(i), 'crumbs')
            for i in page_ids
        ])
