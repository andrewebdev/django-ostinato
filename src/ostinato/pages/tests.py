from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.template.response import SimpleTemplateResponse
from django.utils import simplejson as json
from django.utils import timezone
from django.conf import settings

from ostinato.pages.utils import (get_template_by_name, get_zones_for,
    get_page_zone_by_id)
from ostinato.pages.models import Page, ContentZone
from ostinato.pages.models import PageMeta, BasicTextZone
from ostinato.pages.views import PageView, PageReorderView
from ostinato.pages.admin import inline_factory


## Actual Tests
class UtilsTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']

    def test_get_template_by_name(self):
        self.assertEqual({
            'name': 'basic_page',
            'description': 'A basic template',
            'template': 'pages/tests/basic_page.html',
            'zones': (
                ('meta', 'pages.pagemeta'),
                ('text', 'pages.basictextzone'),
            ),
        }, get_template_by_name('basic_page'))

    def test_get_zones_for(self):
        self.assertEqual(2, len(get_zones_for(Page.objects.get(id=1))))
        expected_list = [
            BasicTextZone.objects.get(id=1),
            BasicTextZone.objects.get(id=3),
        ]
        self.assertEqual(expected_list, get_zones_for(Page.objects.get(id=1)))

    def test_get_page_zone_by_id(self):
        p = Page.objects.get(slug='page-2')
        self.assertEqual(2, get_page_zone_by_id(p, 'text').id)


class PageModelTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    urls = 'ostinato.pages.urls'

    def test_model_exists(self):
        Page

    def test_related_lookup(self):
        u = User.objects.get(username='user1')
        pages = u.pages_authored.all()
        self.assertEqual(2, pages.count())

    def test_unicode(self):
        self.assertEqual('Page 1', Page.objects.get(id=1).__unicode__())

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

    def test_get_zone_by_id(self):
        p = Page.objects.get(slug='page-1')
        self.assertEqual(3, p.get_zone_by_id('contact_info').id)

    def test_get_short_title(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertEqual('Page 1', p.get_short_title())
        self.assertEqual('P2', p2.get_short_title())

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

    def test_absolute_url_based_on_location(self):
        p = Page.objects.get(slug='page-1')
        p3 = Page.objects.create(
            title='Page 3',
            slug='page-3',
            template='landing_page',
            author=User.objects.get(id=1),
            parent=p,
            redirect='http://www.google.com'
        )
        self.assertEqual('http://www.google.com', p3.get_absolute_url())


class PagesStateMachineTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']

    def setUp(self):
        self.p = Page.objects.get(slug='page-1')
        self.p2 = Page.objects.get(slug='page-2')

    def test_has_statemachine(self):
        self.p.sm

    def test_initial_state(self):
        self.assertEqual('private', self.p.sm.state)
        self.assertEqual('private', self.p2.sm.state)

    def test_publish_action(self):
        self.p.sm.take_action('publish')
        self.assertEqual('published', self.p.sm.state)

    def test_publish_action_updates_publish_date(self):
        self.assertEqual(None, self.p.publish_date)

        now = timezone.now()
        self.p.sm.take_action('publish')
        self.p.save()

        ## We need to refresh our page instance, since the publish date
        ## will have updated, but our current instance does not reflect this
        ## change
        self.p = Page.objects.get(id=self.p.id)
        self.assertEqual(now.strftime('%d %m %Y'),
            self.p.publish_date.strftime('%d %m %Y'))

    def test_manager_published(self):
        self.assertFalse(Page.objects.published())
        self.p.sm.take_action('publish')
        self.p.save()

        self.assertEqual(1, Page.objects.published().count())
        self.assertEqual(self.p, Page.objects.published()[0])


class ContentZoneModelTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']

    def test_model_exists(self):
        ContentZone

    def test_is_abstract(self):
        self.assertTrue(ContentZone._meta.abstract)

    def test_zone_subclasses(self):
        PageMeta
        BasicTextZone

    def test_unicode(self):
        z = BasicTextZone.objects.get(id=1)
        self.assertEqual('intro for Page 1', z.__unicode__())
        
    def test_render(self):
        z = BasicTextZone.objects.get(id=1)


class PageManagerTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    urls = 'ostinato.pages.urls'

    def test_get_zones_for_page(self):
        zones = Page.objects.get_zones_for_page(slug='page-1')
        self.assertEqual(2, len(zones))

        # The same method should work withou a slug if we pass a page object
        p = Page.objects.get(slug='page-1')
        zones = Page.objects.get_zones_for_page(page=p)
        self.assertEqual(2, len(zones))

    def test_get_empty_navbar(self):
        empty_nav = Page.objects.get_navbar()
        self.assertEqual([], empty_nav)

    def test_get_navbar(self):
        ## Need to publish the items first
        for p in Page.objects.all():
            p.sm.take_action('publish')
            p.save()

        expected_nav = [{
            'title': u'Page 1',
            'url': '/',
        }, {
            'title': u'P2',
            'url': '/page-2/',
        }]
        self.assertEqual(expected_nav, Page.objects.get_navbar())

        expected_nav = [{
            'title': u'P2',
            'url': '/page-2/',
        }]
        p = Page.objects.get(slug='page-1')
        p.show_in_nav = False
        p.save()
        self.assertEqual(expected_nav, Page.objects.get_navbar())


class PageViewTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    urls = 'ostinato.pages.urls'

    def setUp(self):
        for p in Page.objects.all():
            p.sm.take_action('publish')

    def test_view_exists(self):
        PageView

    def test_reverse_lookup(self):
        self.assertEqual('/', reverse('ostinato_page_home'))
        self.assertEqual('/page-1/',
            reverse('ostinato_page_view', args=['page-1']))

    def test_view_response(self):
        response = self.client.get('/page-1/')

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            'pages/tests/landing_page.html', response.templates[0].name)

    def test_view_context(self):
        response = self.client.get('/page-1/')

        self.assertIn('current_page', response.context)

        # Now for the zones
        self.assertIn('page_zones', response.context)

        zone_instance = BasicTextZone.objects.get(page=1, zone_id='intro')
        self.assertEqual(
            zone_instance, response.context['page_zones']['intro'])
        self.assertEqual(
            'Text Zone 1 Content',
            response.context['page_zones']['intro'].content)


class PageAdminTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    urls = 'ostinato.pages.urls'

    def test_inline_factory(self):
        page = Page.objects.get(slug='page-1')
        inline_factory(BasicTextZone, page)


class NavBarTemplateTagTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    urls = 'ostinato.pages.urls'

    def setUp(self):
        for p in Page.objects.all():
            p.sm.take_action('publish')
            p.save()

        t = Template('{% load pages_tags %}{% navbar %}')
        self.response = SimpleTemplateResponse(t)

    def test_navbar_renders(self):
        self.response.render()
        self.assertTrue(self.response.is_rendered)

    def test_navbar_content(self):
        self.response.render()

        self.assertIn('<li><a class="" href="/">Page 1</a></li>',
            self.response.content)
        self.assertIn('<li><a class="" href="/page-2/">P2</a></li>', 
            self.response.content)


class PageReorderViewTestCase(TransactionTestCase):

    fixtures = ['ostinato_test_fixtures.json', 'ostinato_pages_tests.json']
    url = 'ostinato.pages.urls'

    def test_view_exists(self):
        PageReorderView

    def test_reverse_lookup(self):
        self.assertEqual('/page_reorder/', reverse('ostinato_page_reorder'))

    def test_get_response_not_allowed(self):
        response = self.client.get('/page_reorder/')
        self.assertEqual(405, response.status_code)

    def test_reorder_pages(self):
        """
        TODO: Not sure why these tests are failing when they should pass.
        """
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertEqual(0, p.level)
        self.assertEqual(1, p.lft)
        self.assertEqual(2, p.rght)
        self.assertEqual(1, p.tree_id)

        self.assertEqual(0, p2.level)
        self.assertEqual(3, p2.lft)
        self.assertEqual(4, p2.rght)
        self.assertEqual(2, p.tree_id)

        v = PageReorderView()

        data = {
            'page_moves': [{
                'id': 2,                # Move node id 2 ...
                'position': 'left',     # ... to the Left of ...
                'target': 1,            # ... node id 1
            }]
        }

        v.reorder_pages(data['page_moves'])

        ## Values should now be reversed
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertEqual(0, p.level)
        self.assertEqual(1, p.lft)
        self.assertEqual(2, p.rght)
        self.assertEqual(2, p.tree_id)

        self.assertEqual(0, p2.level)
        self.assertEqual(1, p2.lft)
        self.assertEqual(2, p2.rght)
        self.assertEqual(1, p.tree_id)

    def test_post_response(self):

        data = {
            'page_moves': [{
                'id': 2,                # Move node id 2 ...
                'position': 'left',     # ... to the Left of ...
                'target': 1,            # ... node id 1
            }]
        }

        response = self.client.post('/page_reorder/', data)
        self.assertEqual(302, response.status_code)

