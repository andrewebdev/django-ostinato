from django.test import TestCase, TransactionTestCase
from django.test.client import Client, RequestFactory
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils import simplejson as json
from django.utils import timezone
from django.conf import settings

from ostinato.pages.models import (Page, PageContent, LandingPage, BasicPage,
    ContentMixin)
from ostinato.pages.views import PageView, PageReorderView, page_dispatch


def create_pages():
    user = User.objects.create(username='user1', password='secret',
        email='user1@example.com')

    p = Page.objects.create(
        title="Page 1", slug="page-1",
        author=user, show_in_nav=True,
        created_date = "2012-04-10 12:14:51.203925+00:00",
        modified_date = "2012-04-10 12:14:51.203925+00:00",
        template='pages.landingpage',
    )
    p2 = Page.objects.create(
        title="Page 2", slug="page-2", short_title='P2',
        author=user, show_in_nav=True,
        created_date = "2012-04-10 12:14:51.203925+00:00",
        modified_date = "2012-04-10 12:14:51.203925+00:00",
        template='pages.basicpage',
    )
    p3 = Page.objects.create(
        title="Page 3", slug="page-3", short_title='Page 3',
        author=user, show_in_nav=True,
        created_date = "2012-04-10 12:14:51.203925+00:00",
        modified_date = "2012-04-10 12:14:51.203925+00:00",
        template='pages.basicpage',
        parent=p,
    )

    ## Create some content
    LandingPage.objects.create(
        page=p, intro='Page 1 Introduction', content='Page 1 Content')


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
        self.assertEqual(3, pages.count())

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
        p3 = Page.objects.get(slug='page-3')

        self.assertEqual('/', p.get_absolute_url())  # Root page
        self.assertEqual('/page-2/', p2.get_absolute_url())
        self.assertEqual('/page-1/page-3/', p3.get_absolute_url())

    def test_absolute_url_based_on_location(self):
        p = Page.objects.get(slug='page-1')
        p4 = Page.objects.create(
            title='Page 4', slug='page-4',
            author=User.objects.get(id=1),
            parent=p,
            redirect='http://www.google.com',
        )
        self.assertEqual('http://www.google.com', p4.get_absolute_url())

    def test_get_content_model(self):
        p = Page.objects.get(slug='page-1')
        self.assertEqual(LandingPage, p.get_content_model())

    def test_get_template(self):
        p = Page.objects.get(slug='page-1')
        self.assertEqual('pages/tests/landing_page.html', p.get_template())

    def test_page_contents(self):
        p = Page.objects.get(slug='page-1')
        c = LandingPage.objects.get(id=1)
        self.assertEqual(c, p.contents)


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


class PageContentMixinTestCase(TestCase):

    def test_mixin_exist(self):
        ContentMixin

    def test_has_content_field(self):
        self.assertTrue(ContentMixin._meta.abstract)


class PageContentModelTestCase(TestCase):

    def test_model_exists(self):
        PageContent

    def test_model_is_abstract(self):
        self.assertTrue(PageContent._meta.abstract)

    def test_template_meta(self):
        PageContent.ContentOptions


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

    def test_get_breadcrumbs(self):
        for p in Page.objects.all():
            p.sm.take_action('publish')
            p.save()

        expected_crumbs = [{
            'title': u'Page 1',
            'url': '/',
        }, {
            'title': u'Page 3',
            'url': '/page-1/page-3/',
        }]
        p = Page.objects.get(slug='page-3')
        self.assertEqual(expected_crumbs, Page.objects.get_breadcrumbs(p))


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
        self.assertIn('page', response.context)

    def test_view_content(self):
        response = self.client.get('/page-1/')
        self.assertIn('Page 1 Content', response.content)


class ViewDispatcherTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

        for p in Page.objects.all():
            p.sm.take_action('publish')

    def test_dispatcher_exists(self):
        page_dispatch

    def test_returns_valid_view(self):
        rf = RequestFactory()
        request = rf.get('/page-1/')

        response = page_dispatch(request)
        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response, TemplateResponse)

    def test_custom_view_response(self):
        response = self.client.get('/page-2/')

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            'pages/tests/basic_page.html', response.templates[0].name)

    def test_custom_view_context(self):
        response = self.client.get('/page-2/')

        self.assertIn('page', response.context)
        self.assertIn('custom', response.context)
        self.assertEqual('Some Custom Context', response.context['custom'])


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


class GetPageTemplateTagTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()
        t = Template('{% load pages_tags %}{% get_page "page-1" as somepage %}{{ somepage }}')
        self.response = SimpleTemplateResponse(t)

    def test_tag_renders(self):
        self.response.render()
        self.assertTrue(self.response.is_rendered)

    def test_page_in_content(self):
        self.response.render()
        self.assertIn('Page 1', self.response.content)


class BreadCrumbsTempalteTagTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()
        t = Template('{% load pages_tags %}{% get_page "page-3" as page %}{% breadcrumbs %}')
        self.response = SimpleTemplateResponse(t)

    def test_tag_renders(self):
        self.response.render()
        self.assertTrue(self.response.is_rendered)

    def test_breadcrumbs_in_context(self):
        self.response.render()
        self.assertIn('<a href="/">Page 1</a> &gt;&gt; ', self.response.content)
        self.assertIn('<strong>Page 3</strong>', self.response.content)


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
            'node': 2,              # Move node id 2 ...
            'position': 'left',     # ... to the Left of ...
            'target': 1,            # ... node id 1
        }

        response = self.client.post('/page_reorder/', data)
        self.assertEqual(302, response.status_code)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertGreater(p.tree_id, p2.tree_id)


