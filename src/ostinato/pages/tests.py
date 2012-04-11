from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from ostinato.pages.pages_registry import page_templates, PageTemplate
from ostinato.pages.models import Page, ZoneContent, get_template_choices
from ostinato.pages.models import PageMeta, BasicTextZone
from ostinato.pages.views import PageView


## Register some Page Templates
@page_templates.register
class BasicPage(PageTemplate):
    template_id = 'basic_page'
    description = 'A basic template'
    template = 'pages/tests/basic_page.html'
    zones = (
        ('meta', 'pages.pagemeta'),
        ('text', 'pages.basictextzone'),
    )


@page_templates.register
class LandingPage(PageTemplate):
    template_id = 'landing_page'
    description = 'An Index Page'
    template = 'pages/tests/landing_page.html'
    zones = (
        ('intro', 'pages.basictextzone'),
        ('contact_info', 'pages.basictextzone'),
    )


## Actual Tests
class PageTemplateTestCase(TestCase):

    def test_page_template_class(self):
        PageTemplate

    def test_templates_in_registry(self):
        classes = page_templates.all()
        self.assertIn(LandingPage, classes)
        self.assertIn(BasicPage, classes)

    def test_get_template_by_id(self):
        self.assertEqual(BasicPage,
            PageTemplate.get_template_by_id('basic_page'))

    def test_get_template_by_id_invalid(self):
        self.assertEqual(None, PageTemplate.get_template_by_id('invalid'))


class PageModelTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    urls = 'ostinato.pages.urls'

    def test_model_exists(self):
        Page

    def test_related_lookup(self):
        u = User.objects.get(username='user1')
        pages = u.pages_authored.all()
        self.assertEqual(2, pages.count())

    def test_page_template_choices(self):
        p = Page.objects.get(id=1)
        self.assertIn(('basic_page', 'A basic template'), get_template_choices())
        self.assertIn(('landing_page', 'An Index Page'), get_template_choices())

    def test_page_template_order(self):
        self.assertTrue(False,
            'TODO: we need a way to order the templates after they were registered.')

    def test_get_zones(self):
        p = Page.objects.get(slug='page-1')
        zones = [zone for zone in p.get_zones()]

        self.assertEqual(2, len(zones))

        ## A couple of very explicit tests
        self.assertEqual(1, zones[0].id)
        self.assertEqual('intro', zones[0].zone_id)

        self.assertEqual(3, zones[1].id)
        self.assertEqual('contact_info', zones[1].zone_id)

        ## A second page should create new zones for that page
        p = Page.objects.get(slug='page-2')
        zones = [zone for zone in p.get_zones()]

        self.assertEqual(2, len(zones))

        ## A couple of very explicit tests
        self.assertEqual(1, zones[0].id)
        self.assertEqual('meta', zones[0].zone_id)

        self.assertEqual(2, zones[1].id)
        self.assertEqual('text', zones[1].zone_id)

    def test_absolute_url(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertEqual('/', p.get_absolute_url())  # Root page
        self.assertEqual('/page-2/', p2.get_absolute_url())

        ## Test nested pages
        p3 = Page.objects.create(
            title='Page 3',
            slug='page-3',
            template='landing_page',
            author=User.objects.get(id=1),
            parent=p
        )
        self.assertEqual('/page-1/page-3/', p3.get_absolute_url())


class ZoneContentModelTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']

    def test_model_exists(self):
        ZoneContent

    def test_is_abstract(self):
        self.assertTrue(ZoneContent._meta.abstract)

    def test_zone_subclasses(self):
        PageMeta
        BasicTextZone


class PageManagerTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']

    def test_get_zones_for_page(self):
        zones = Page.objects.get_zones_for_page(slug='page-1')
        self.assertEqual(2, len(zones))

        # The same method should work withou a slug if we pass a page object
        p = Page.objects.get(slug='page-1')
        zones = Page.objects.get_zones_for_page(page=p)
        self.assertEqual(2, len(zones))


class PageViewTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    urls = 'ostinato.pages.urls'

    def test_view_exists(self):
        PageView

    def test_reverse_lookup(self):
        self.assertEqual('/', reverse('ostinato_page_home'))
        self.assertEqual('/page-1/',
            reverse('ostinato_page_view', args=['page-1']))

    def test_view_response(self):
        c = Client()
        response = c.get('/page-1/')

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            'pages/tests/landing_page.html', response.templates[0].name)

    def test_view_context(self):
        c = Client()
        response = c.get('/page-1/')

        self.assertIn('current_page', response.context)

        # Now for the zones
        self.assertIn('page_zones', response.context)

        zone_instance = BasicTextZone.objects.get(page=1, zone_id='intro')
        self.assertEqual(
            zone_instance, response.context['page_zones']['intro'])
        self.assertEqual(
            'Text Zone 1 Content',
            response.context['page_zones']['intro'].content)

