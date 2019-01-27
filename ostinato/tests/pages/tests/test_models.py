from django.test import TestCase
from django.core.cache import caches

from ostinato.pages.models import (
    get_content_model,
    get_template_options,
    Page,
    PageContent
)

from ostinato.tests.pages.models import LandingPage, Contributor

from .utils import create_pages


# Actual Tests
class TemplateRegistryTestCase(TestCase):

    def test_get_content_model(self):
        content_model = get_content_model('pages.landingpage')
        self.assertEqual(LandingPage, content_model)

    def test_get_template_options(self):
        opts = get_template_options('pages.basicpage')
        self.assertEqual(opts, {
            'label': 'Basic Page',
            'template': 'pages/basic_page.html',
            'view': 'ostinato.tests.pages.views.CustomView',
            'admin_form': 'ostinato.tests.pages.admin.BasicPageAdminForm',
            'page_inlines': [
                'ostinato.tests.pages.models.ContributorInline',
            ]
        })


class PageModelTestCase(TestCase):

    def setUp(self):
        create_pages()

    def test_str(self):
        self.assertEqual('Page 1', str(Page.objects.get(id=1)))

    def test_get_short_title(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertEqual('Page 1', p.get_short_title())
        self.assertEqual('P2', p2.get_short_title())

    def test_absolute_url(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        p3 = Page.objects.get(slug='page-3')

        self.assertEqual('/', p.get_absolute_url())  # Root page
        self.assertEqual('/page-2', p2.get_absolute_url())
        self.assertEqual('/page-1/page-3', p3.get_absolute_url())

    def test_absolute_url_is_cached(self):
        p3 = Page.objects.get(slug='page-3')
        cache = caches['default']
        cache_key = 'ostinato:pages:page:3:url'

        # First the get_absolute_url should cache the url
        # Lets make sure that this url wasn't previously cached
        cache.set(cache_key, None)
        self.assertEqual('/page-1/page-3', p3.get_absolute_url())
        self.assertEqual('/page-1/page-3', cache.get(cache_key))

    def test_absolute_url_clear_cache(self):
        p3 = Page.objects.get(slug='page-3')
        p3.get_absolute_url(clear_cache=True)

    def test_urls_recached_after_page_delete(self):
        p3 = Page.objects.get(slug='page-3')
        cache = caches['default']
        url_key = 'ostinato:pages:page:3:url'
        crumbs_key = 'ostinato:pages:page:3:crumbs'

        # create some dummy cache values
        cache.set(url_key, 'URL-Cache-Value', 60 * 60 * 24 * 7 * 4)
        cache.set(crumbs_key, 'Crumbs-Cache-Value', 60 * 60 * 24 * 7 * 4)

        # Lets make sure that this url wasn't previously cached
        self.assertEqual('URL-Cache-Value', cache.get(url_key))
        self.assertEqual('Crumbs-Cache-Value', cache.get(crumbs_key))

        # Delete P3
        p3.delete()

        # the cache should now be re-generated
        self.assertEqual(None, cache.get(url_key))
        self.assertEqual(None, cache.get(crumbs_key))

    def test_urls_updated_after_move(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        p3 = Page.objects.get(slug='page-3')
        p3.parent = p2
        p3.save()

        self.assertEqual('/page-2/page-3', p3.get_absolute_url())

        # We need to test a couple of other moves also, just to make sure
        # changes are propagated up the tree
        # p2.move_to(p, position='first-child')
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        p3 = Page.objects.get(slug='page-3')
        p2.parent = p
        p2.save()

        # Get fresh variables so that mptt does the right thing
        p2 = Page.objects.get(slug='page-2')
        self.assertEqual('/page-1/page-2', p2.get_absolute_url())

        p3 = Page.objects.get(slug='page-3')
        self.assertEqual('/page-1/page-2/page-3', p3.get_absolute_url())

    def test_absolute_url_based_on_location(self):
        p = Page.objects.get(slug='page-1')
        p4 = Page.objects.create(
            title='Page 4', slug='page-4', parent=p,
            redirect='http://www.google.com')
        self.assertEqual('http://www.google.com', p4.get_absolute_url())

    def test_get_template(self):
        p = Page.objects.get(slug='page-1')
        self.assertEqual('pages/landing_page.html', p.get_template())

    def test_get_template_when_none(self):
        p = Page.objects.get(slug='other-page')
        self.assertEqual('pages/pages_otherpage.html', p.get_template())

    def test_page_contents(self):
        p = Page.objects.get(slug='page-1')
        c = LandingPage.objects.get(id=1)
        self.assertEqual(c, p.contents)


class PageContentModelTestCase(TestCase):

    def test_model_is_abstract(self):
        self.assertTrue(PageContent._meta.abstract)

    def test_inline_content_for_page(self):
        create_pages()

        p = Page.objects.get(slug='page-3')
        Contributor.objects.create(page=p, name='Contributor 1')

        qs = Contributor.objects.filter(page=p)
        self.assertEqual(qs[0], p.testing.all()[0])
