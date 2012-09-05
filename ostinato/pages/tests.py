from django.test import TestCase, TransactionTestCase
from django.test.client import Client, RequestFactory
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils import simplejson as json
from django.utils import timezone
from django.conf import settings

from ostinato.pages.registry import page_content
from ostinato.pages.models import Page, PageContent
from ostinato.pages.views import PageView, PageReorderView, page_dispatch


page_content.setup()  # Clear the registry before we start the tests


## Create some Page Content
class Contributor(models.Model):
    page = models.ForeignKey(Page, related_name='testing')
    name = models.CharField(max_length=50)

class ContributorInline(admin.StackedInline):
    model = Contributor


class ContentMixin(models.Model):
    """
    An example of how you would do mixins. A mixin must be an abstract
    model.
    """
    content = models.TextField()

    class Meta:
        abstract = True  # Required for mixins


@page_content.register
class LandingPage(ContentMixin, PageContent):
    intro = models.TextField()

    class ContentOptions:
        template = 'pages/tests/landing_page.html'


@page_content.register
class BasicPage(ContentMixin, PageContent):

    class ContentOptions:
        template = 'pages/tests/basic_page.html'
        view = 'ostinato.pages.views.CustomView'
        page_inlines = ['ostinato.pages.tests.ContributorInline']


@page_content.register
class OtherPage(ContentMixin, PageContent):
    """ Test content that doesn't have a template specified """

    class Meta:
        verbose_name = 'Some Other Page'

 
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
class ContentRegistryTestCase(TestCase):

    def test_content_registered(self):
        self.assertEqual(3, len(page_content.all()))

    def test_content_class_in_registry(self):
        self.assertIn(BasicPage, page_content.all())

    def test_get_template_choices(self):
        self.assertEqual((
            ('', '--------'),
            ('pages.landingpage', 'Pages | Landing Page'),
            ('pages.basicpage', 'Pages | Basic Page'),
            ('pages.otherpage', 'Pages | Some Other Page'),
        ), page_content.get_template_choices())

    def test_get_template_name(self):
        self.assertEqual('Pages | Basic Page',
            page_content.get_template_name('pages.basicpage'))


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


class PageManagerTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

    def test_published(self):
        self.assertEqual([1, 2, 3],
            list(Page.objects.published().values_list('id', flat=True)))

    def test_get_empty_navbar(self):
        Page.objects.published().update(state=1)
        empty_nav = Page.objects.get_navbar()
        self.assertEqual([], empty_nav)

    def test_get_navbar(self):
        expected_nav = [{
            'slug': u'page-1',
            'title': u'Page 1',
            'url': '/',
        }, {
            'slug': u'page-2',
            'title': u'P2',
            'url': '/page-2/',
        }]
        self.assertEqual(expected_nav, Page.objects.get_navbar())

        expected_nav = [{
            'slug': u'page-2',
            'title': u'P2',
            'url': '/page-2/',
        }]
        p = Page.objects.get(slug='page-1')
        p.show_in_nav = False
        p.save()
        self.assertEqual(expected_nav, Page.objects.get_navbar())

    def test_get_breadcrumbs(self):
        expected_crumbs = [{
            'slug': u'page-1',
            'title': u'Page 1',
            'url': '/',
        }, {
            'slug': u'page-3',
            'title': u'Page 3',
            'url': '/page-1/page-3/',
        }]
        p = Page.objects.get(slug='page-3')
        self.assertEqual(expected_crumbs, Page.objects.get_breadcrumbs(p))

    def test_get_page_from_path(self):
        rf = RequestFactory()
        request = rf.get('/page-1/page-3/')

        self.assertEqual('page-3',
            Page.objects.get_from_path(request.path).slug)


class PageContentModelTestCase(TestCase):

    def test_model_exists(self):
        PageContent

    def test_model_is_abstract(self):
        self.assertTrue(PageContent._meta.abstract)

    def test_content_options(self):
        PageContent.ContentOptions

    def test_get_template(self):
        create_pages()
        p = Page.objects.get(slug='page-1')
        self.assertEqual('pages/tests/landing_page.html', p.get_template())

    def test_get_template_when_none(self):
        p = Page.objects.create(title='Test Page', slug='test-page',
            template='pages.otherpage')
        self.assertEqual('pages/other_page.html', p.get_template())

    def test_add_content(self):
        create_pages()
        p = Page.objects.get(slug='page-1')
        p.contents.add_content(something='Some Content')
        self.assertEqual('Some Content', p.contents.something)

    def test_inline_content_for_page(self):
        create_pages()
        p = Page.objects.get(slug='page-3')
        content = BasicPage.objects.create(page=p, content='Page 3 Content')
        Contributor.objects.create(page=p, name='Contributor 1')

        qs = Contributor.objects.filter(page=p)
        self.assertEqual(qs[0], p.contents.contributor_set[0])


class PageViewTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

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

        t = Template('{% load pages_tags %}{% navbar %}')
        self.response = SimpleTemplateResponse(t)

    def test_navbar_renders(self):
        self.response.render()
        self.assertTrue(self.response.is_rendered)

    def test_navbar_content(self):
        self.response.render()

        self.assertIn('<a href="/">Page 1</a>',
            self.response.content)
        self.assertIn('<a href="/page-2/">P2</a>', 
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

    def test_staff_only(self):
        data = {
            'node': 2,              # Move node id 2 ...
            'position': 'left',     # ... to the Left of ...
            'target': 1,            # ... node id 1
        }
        response = self.client.post('/page_reorder/', data)
        self.assertEqual(200, response.status_code)
        self.assertIn('value="Log in"', response.content)

    def test_post_response(self):

        # We need a logged in user
        u = User.objects.create(username='tester', password='',
            email='test@example.com')
        u.is_staff = True
        u.set_password('secret')
        u.save()

        login = self.client.login(username='tester', password='secret')
        self.assertTrue(login)

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


