from django.test import TestCase
from django.test.client import RequestFactory
from django.core.cache import caches

from ostinato.pages.models import Page

from .utils import create_pages


class PageManagerTestCase(TestCase):

    def setUp(self):
        create_pages()

    def test_published(self):
        self.assertEqual(
            [1, 3, 2, 4],
            list(Page.objects.published().values_list('id', flat=True)))

    def test_get_breadcrumbs(self):
        expected_crumbs = [{
            'slug': u'page-1',
            'title': u'Page 1',
            'url': '/',
        }, {
            'slug': u'page-3',
            'title': u'Page 3',
            'url': '/page-1/page-3',
        }]
        p = Page.objects.get(slug='page-3')
        self.assertEqual(
            expected_crumbs,
            Page.objects.get_breadcrumbs(p, clear_cache=True)
        )

    def test_get_page_from_path(self):
        rf = RequestFactory()
        request = rf.get('/page-1/page-3')
        self.assertEqual(
            'page-3',
            Page.objects.get_from_path(request.path, clear_cache=True).slug
        )

    def test_get_page_from_path_returns_none(self):
        rf = RequestFactory()
        request = rf.get('/no/pages/on/path/')
        self.assertIsNone(Page.objects.get_from_path(request.path))

    def test_generate_url_cache(self):
        cache = caches['default']

        def cache_url(id):
            return cache.get('ostinato:pages:page:{0}:url'.format(id))

        # Make sure the url cache is empty
        for i in range(3):
            cache.set('ostinato:pages:page:{0}:url'.format(i), None)

        Page.objects.generate_url_cache()

        self.assertEqual('/', cache_url(1))
        self.assertEqual('/page-2', cache_url(2))
        self.assertEqual('/page-1/page-3', cache_url(3))

    def test_clear_url_cache(self):
        cache = caches['default']

        def cache_url(id):
            return cache.get('ostinato:pages:page:{0}:url'.format(id))

        Page.objects.generate_url_cache()  # Make sure there is a cache
        Page.objects.clear_url_cache()

        self.assertEqual(None, cache_url(1))
        self.assertEqual(None, cache_url(2))
        self.assertEqual(None, cache_url(3))
