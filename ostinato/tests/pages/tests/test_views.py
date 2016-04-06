from django.test import TestCase, TransactionTestCase
from django.test.client import RequestFactory

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.template.response import TemplateResponse

from ostinato.pages.models import Page
from ostinato.pages.views import (
    PageView,
    page_dispatch,
    PageReorderView,
    PageDuplicateView,
)
from ostinato.pages.forms import DuplicatePageForm
from .utils import *
from .factories import *


class PageViewTestCase(TestCase):

    def setUp(self):
        create_pages()

    def tearDown(self):
        self.client.logout()

    def test_view_exists(self):
        PageView

    def test_reverse_lookup(self):
        self.assertEqual('/', reverse('ostinato_page_home'))
        self.assertEqual(
            '/page-1/', reverse('ostinato_page_view', args=['page-1']))

    def test_view_response(self):
        response = self.client.get('/page-1/')
        self.assertEqual(200, response.status_code)
        self.assertEqual('pages/landing_page.html',
                         response.templates[0].name)

    def test_view_context(self):
        response = self.client.get('/page-1/')
        self.assertIn('page', response.context)

    def test_view_content(self):
        response = self.client.get('/page-1/')
        self.assertIn('Page 1 Content', response.content)

    def test_function_based_view(self):
        response = self.client.get('/func-page/')
        self.assertEqual(200, response.status_code)

    def test_unauthorized_user_raises_forbidden(self):
        # First we make the page private
        p = Page.objects.get(slug='page-1')
        p.state = 1
        p.save()

        response = self.client.get('/page-1/')
        self.assertEqual(403, response.status_code)

    def test_superuser_can_access_private_page(self):
        # First we make the page private
        p = Page.objects.get(slug='page-1')
        p.state = 1
        p.save()

        # Make a second user, which is a superuser
        u = User.objects.create(
            username='not_an_author',
            password="secret",
            email="naa@example.com")
        u.set_password("secret")
        u.is_superuser = True
        u.save()

        self.client.login(username='not_an_author', password='secret')
        response = self.client.get('/page-1/')
        self.assertEqual(200, response.status_code)


class SitesEnabledPageViewTestCase(TestCase):

    def setUp(self):
        create_pages()

    def test_view_respsponse(self):
        response = self.client.get('/page-1/')

        with self.settings(OSTINATO_PAGES_SITE_TREEID=1):
            self.assertEqual(200, response.status_code)
            self.assertEqual(
                'pages/landing_page.html', response.templates[0].name)

    def test_different_site_page_returns_404(self):
        # Without sites enabled, respond as normal
        response = self.client.get('/page-2/')
        self.assertEqual(200, response.status_code)

        # With sites enabled this should raise 404
        with self.settings(OSTINATO_PAGES_SITE_TREEID=1):
            response = self.client.get('/page-2/')
            self.assertEqual(404, response.status_code)

    def test_root_page_for_site(self):
        with self.settings(OSTINATO_PAGES_SITE_TREEID=2, DEBUG=True):
            response = self.client.get('/')
            self.assertEqual(200, response.status_code)
            self.assertEqual('page-2', response.context['page'].slug)


class ViewDispatcherTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

    def test_returns_valid_view(self):
        rf = RequestFactory()
        request = rf.get('/page-1/')
        request.user = AnonymousUser()
        response = page_dispatch(request)
        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response, TemplateResponse)

    def test_custom_view_response(self):
        response = self.client.get('/page-2/')

        self.assertEqual(200, response.status_code)
        self.assertEqual('pages/basic_page.html', response.templates[0].name)

    def test_custom_view_context(self):
        response = self.client.get('/page-2/')

        self.assertIn('page', response.context)
        self.assertIn('custom', response.context)
        self.assertEqual('Some Custom Context', response.context['custom'])


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

    def test_staff_only(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        data = {
            'node': p2.id,          # Move node id 2 ...
            'position': 'left',     # ... to the Left of ...
            'target': p.id,         # ... node id 1
        }
        response = self.client.post('/page_reorder/', data)

        # FIXME: This isn't a proper test
        self.assertEqual(302, response.status_code)
        # self.assertIn('value="Log in"', response.content)

    def test_post_response(self):
        # We need a logged in user
        u = User.objects.create(
            username='tester', password='', email='test@example.com')
        u.is_staff = True
        u.set_password('secret')
        u.save()
        login = self.client.login(username='tester', password='secret')
        self.assertTrue(login)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertLess(p.tree_id, p2.tree_id)

        data = {
            'node': p2.id,          # Move node id 2 ...
            'position': 'left',     # ... to the Left of ...
            'target': p.id,         # ... node id 1
        }

        response = self.client.post('/page_reorder/', data)
        self.assertEqual(302, response.status_code)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertGreater(p.tree_id, p2.tree_id)


class PageDuplicateViewTestCase(TransactionTestCase):

    def setUp(self):
        create_pages()

    def test_view_exists(self):
        PageDuplicateView

    def test_reverse_lookup(self):
        self.assertEqual('/page_duplicate/', reverse('ostinato_page_duplicate'))

    def test_get_response_not_allowed(self):
        response = self.client.get('/page_duplicate/')
        self.assertEqual(405, response.status_code)

    def test_staff_only(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        data = {
            'node': p2.id,          # Move node id 2 ...
            'position': 'left',     # ... to the Left of ...
            'target': p.id,         # ... node id 1
        }
        response = self.client.post('/page_duplicate/', data)
        # FIXME: This isn't a proper test
        self.assertEqual(302, response.status_code)
        # self.assertIn('value="Log in"', response.content)

    def test_post_response(self):
        u = User.objects.create(
            username='tester', password='', email='test@example.com')
        u.is_staff = True
        u.set_password('secret')
        u.save()

        login = self.client.login(username='tester', password='secret')
        self.assertTrue(login)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        self.assertLess(p.tree_id, p2.tree_id)

        data = {
            'node': p2.id,           # Select Node id 2 ...
            'position': 'right',     # ... duplicate to the right of ...
            'target': p2.id,         # ... node id 2 (myself)
        }

        response = self.client.post('/page_duplicate/', data)
        self.assertEqual(302, response.status_code)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        p3 = Page.objects.get(slug='page-2-copy')

        self.assertGreater(p3.tree_id, p2.tree_id)
        self.assertEqual('Page 2', p3.title)

    def test_page_content_is_also_duplicated(self):
        u = User.objects.create(
            username='tester', password='', email='test@example.com')
        u.is_staff = True
        u.set_password('secret')
        u.save()

        login = self.client.login(username='tester', password='secret')
        self.assertTrue(login)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        BasicPageFactory.create(page=p2)

        data = {
            'node': p2.id,           # Select Node id 2 ...
            'position': 'right',     # ... duplicate to the right of ...
            'target': p2.id,         # ... node id 2 (myself)
        }
        form = DuplicatePageForm(data)
        if form.is_valid():
            form.save()

        p3 = Page.objects.get(slug='page-2-copy')
        self.assertEqual(
            'Some content for the page', p3.contents.content)

