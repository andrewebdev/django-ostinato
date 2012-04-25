from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.template.response import SimpleTemplateResponse
from django.utils import simplejson as json
from django.utils import timezone
from django.conf import settings

from ostinato.pages.models import Page, PageTemplate
from ostinato.pages.views import PageView, PageReorderView
from ostinato.pages.admin import inline_factory


class LandingPage(PageTemplate):
    intro = models.TextField()

    class TemplateMeta:
        template = 'pages/tests/landing_page.html'


class BasicPage(PageTemplate):
    class TemplateMeta:
        template = 'pages/tests/basic_page.html'


def create_pages():
    user = User.objects.create(username='user1', password='secret',
        email='user1@example.com')

    Page.objects.create(
        title="Page 1", slug="page-1",
        author=user, show_in_nav=True,
        created_date = "2012-04-10 12:14:51.203925+00:00",
        modified_date = "2012-04-10 12:14:51.203925+00:00",
        content=LandingPage.objects.create(intro='Page 1 Introduction')
    )
    Page.objects.create(
        title="Page 2", slug="page-2", short_title='P2',
        author=user, show_in_nav=True,
        created_date = "2012-04-10 12:14:51.203925+00:00",
        modified_date = "2012-04-10 12:14:51.203925+00:00",
        content=LandingPage.objects.create()
    )


## Actual Tests

class PageModelTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

    def test_model_exists(self):
        Page

    def test_related_lookup(self):
        u = User.objects.get(username='user1')
        pages = u.pages_authored.all()
        self.assertEqual(2, pages.count())

    def test_unicode(self):
        self.assertEqual('Page 1', Page.objects.get(id=1).__unicode__())

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
            author=User.objects.get(id=1),
            parent=p,
            content=BasicPage.objects.create()
        )
        self.assertEqual('/page-1/page-3/', p3.get_absolute_url())

    def test_absolute_url_based_on_location(self):
        p = Page.objects.get(slug='page-1')
        p3 = Page.objects.create(
            title='Page 3', slug='page-3',
            author=User.objects.get(id=1),
            parent=p,
            redirect='http://www.google.com',
            content=BasicPage.objects.create(),
        )
        self.assertEqual('http://www.google.com', p3.get_absolute_url())


class PagesStateMachineTestCase(TestCase):

    def setUp(self):
        create_pages()

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


class PageTemplateModelTestCase(TestCase):

    def test_model_exists(self):
        PageTemplate

    def test_model_is_abstract(self):
        self.assertTrue(PageTemplate._meta.abstract)

    def test_template_meta(self):
        PageTemplate.TemplateMeta


class CustomTemplateModelTestCase(TestCase):

    def test_get_template(self):
        self.assertEqual(
            ('pages/tests/landing_page.html', 'landing page'),
            LandingPage.get_template())


class PageManagerTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

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

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

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

    def test_content(self):
        response = self.client.get('/page-1/')

        content = LandingPage.objects.get(id=1)

        self.assertEqual(content, response.context['current_page'].content)
        self.assertEqual('Page 1 Introduction',
            response.context['current_page'].content.intro)


class NavBarTemplateTagTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

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

    url = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

    def test_view_exists(self):
        PageReorderView

    def test_reverse_lookup(self):
        self.assertEqual('/page_reorder/', reverse('ostinato_page_reorder'))

    def test_get_response_not_allowed(self):
        response = self.client.get('/page_reorder/')
        self.assertEqual(405, response.status_code)

    def test_post_response(self):

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertLess(p.tree_id, p2.tree_id)

        data = {
            'node': 2,                # Move node id 2 ...
            'position': 'left',     # ... to the Left of ...
            'target': 1,            # ... node id 1
        }

        response = self.client.post('/page_reorder/', data)
        self.assertEqual(302, response.status_code)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertGreater(p.tree_id, p2.tree_id)

