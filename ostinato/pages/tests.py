from django.test import TestCase, TransactionTestCase
from django.test.client import RequestFactory
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.core.cache import get_cache
from django.template import Context, Template
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django import http

from ostinato.pages.registry import page_content
from ostinato.pages.models import Page, PageContent, ContentError
from ostinato.pages.views import PageView, PageReorderView, page_dispatch
from ostinato.pages.templatetags.pages_tags import (
    get_page, filter_pages, breadcrumbs)


page_content.setup()  # Clear the registry before we start the tests


## Create some Page Content
class Photo(models.Model):
    photo_path = models.CharField(max_length=250)


class Contributor(models.Model):
    page = models.ForeignKey(Page, related_name='testing')
    name = models.CharField(max_length=50)

    ## Required to test the inlines with through model
    photos = models.ManyToManyField(
        Photo, through='ContributorPhotos', null=True, blank=True)


class ContributorPhotos(models.Model):
    contributor = models.ForeignKey(Contributor)
    photo = models.ForeignKey(Photo)
    order = models.IntegerField(default=1)


class ContributorInline(admin.StackedInline):
    model = Contributor


class PhotoInline(admin.StackedInline):
    model = Contributor.photos.through


class ContentMixin(models.Model):
    """
    An example of how you would do mixins. A mixin must be an abstract
    model.
    """
    content = models.TextField()

    class Meta:
        abstract = True  # Required for mixins


def functionview(request, *args, **kwargs):
    return http.HttpResponse('ok')


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
        admin_inlines = [
            'ostinato.pages.tests.ContributorInline',
        ]


@page_content.register
class BasicPageFunc(ContentMixin, PageContent):
    """
    A page that makes use of the old school function based views.
    """
    class ContentOptions:
        template = 'pages/test/basic_page.html'
        view = 'ostinato.pages.tests.functionview'


@page_content.register
class OtherPage(ContentMixin, PageContent):
    """ Test content that doesn't have a template specified """

    class Meta:
        verbose_name = 'Some Other Page'


def create_pages():
    user = User.objects.create(
        username='user1', password='secret', email='user1@example.com')

    p = Page.objects.create(
        title="Page 1", slug="page-1",
        author=user, show_in_nav=True,
        created_date="2012-04-10 12:14:51.203925+00:00",
        modified_date="2012-04-10 12:14:51.203925+00:00",
        template='pages.landingpage',
    )
    Page.objects.create(
        title="Page 2", slug="page-2", short_title='P2',
        author=user, show_in_nav=True,
        created_date="2012-04-10 12:14:51.203925+00:00",
        modified_date="2012-04-10 12:14:51.203925+00:00",
        template='pages.basicpage',
    )
    Page.objects.create(
        title="Page 3", slug="page-3", short_title='Page 3',
        author=user, show_in_nav=True,
        created_date="2012-04-10 12:14:51.203925+00:00",
        modified_date="2012-04-10 12:14:51.203925+00:00",
        template='pages.basicpage',
        parent=p,
    )
    Page.objects.create(
        title="Page 1", slug="func-page",
        author=user, show_in_nav=False,
        created_date="2012-04-10 12:14:51.203925+00:00",
        modified_date="2012-04-10 12:14:51.203925+00:00",
        template='pages.basicpagefunc',
    )

    ## Create some content
    LandingPage.objects.create(
        page=p, intro='Page 1 Introduction', content='Page 1 Content')


## Actual Tests
class ContentRegistryTestCase(TestCase):

    def test_content_registered(self):
        self.assertEqual(4, len(page_content.all()))

    def test_content_class_in_registry(self):
        self.assertIn(BasicPage, page_content.all())

    def test_get_template_choices(self):
        self.assertEqual((
            ('', '--------'),
            ('pages.landingpage', 'Pages | Landing Page'),
            ('pages.basicpage', 'Pages | Basic Page'),
            ('pages.basicpagefunc', 'Pages | Basic Page Func'),
            ('pages.otherpage', 'Pages | Some Other Page'),
        ), page_content.get_template_choices())

    def test_get_template_name(self):
        self.assertEqual(
            'Pages | Basic Page',
            page_content.get_template_name('pages.basicpage'))

    def test_get_template_name_invalid_id(self):
        self.assertEqual(
            'invalid.content',
            page_content.get_template_name('invalid.content'))


class PageModelTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

    def test_model_exists(self):
        Page

    def test_related_lookup(self):
        u = User.objects.get(username='user1')
        pages = u.pages_authored.all()
        self.assertEqual(4, pages.count())

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

    def test_absolute_url_is_cached(self):
        p3 = Page.objects.get(slug='page-3')
        cache = get_cache('default')
        cache_key = 'ostinato:pages:page:3:url'

        # First the get_absolute_url should cache the url
        # Lets make sure that this url wasn't previously cached
        cache.set(cache_key, None)
        self.assertEqual('/page-1/page-3/', p3.get_absolute_url())
        self.assertEqual('/page-1/page-3/', cache.get(cache_key))

    def test_absolute_url_clear_cache(self):
        p3 = Page.objects.get(slug='page-3')
        p3.get_absolute_url(clear_cache=True)

    def test_urls_updated_after_move(self):
        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')
        p3 = Page.objects.get(slug='page-3')
        p3.parent = p2
        p3.save()

        self.assertEqual('/page-2/page-3/', p3.get_absolute_url())

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
        self.assertEqual('/page-1/page-2/', p2.get_absolute_url())

        p3 = Page.objects.get(slug='page-3')
        self.assertEqual('/page-1/page-2/page-3/', p3.get_absolute_url())

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
        self.assertEqual(
            [1, 3, 2, 4],
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
            'level': 0,
            'tree_id': 1,
        }, {
            'slug': u'page-2',
            'title': u'P2',
            'url': '/page-2/',
            'level': 0,
            'tree_id': 2,
        }]
        self.assertEqual(expected_nav, Page.objects.get_navbar(clear_cache=True))

        expected_nav = [{
            'slug': u'page-2',
            'title': u'P2',
            'url': '/page-2/',
            'level': 0,
            'tree_id': 2,
        }]
        p = Page.objects.get(slug='page-1')
        p.show_in_nav = False
        p.save()
        self.assertEqual(expected_nav, Page.objects.get_navbar())

    def test_get_navbar_for_page(self):
        expected_nav = [{
            'slug': u'page-3',
            'title': u'Page 3',
            'url': '/page-1/page-3/',
            'level': 1,
            'tree_id': 1,
        }]
        self.assertEqual(
            expected_nav,
            Page.objects.get_navbar(
                for_page=Page.objects.get(slug='page-1'),
                clear_cache=True))

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
        self.assertEqual(expected_crumbs, Page.objects.get_breadcrumbs(
            p, clear_cache=True))

    def test_get_page_from_path(self):
        rf = RequestFactory()
        request = rf.get('/page-1/page-3/')
        self.assertEqual(
            'page-3',
            Page.objects.get_from_path(request.path, clear_cache=True).slug)

    def test_get_page_from_path_returns_none(self):
        rf = RequestFactory()
        request = rf.get('/no/pages/on/path/')
        self.assertIsNone(Page.objects.get_from_path(request.path))

    def test_generate_url_cache(self):
        cache = get_cache('default')
        cache_url = lambda id: cache.get('ostinato:pages:page:%s:url' % id)

        # Make sure the url cache is empty
        for i in range(3):
            cache.set('ostinato:pages:page:%s:url' % i, None)

        Page.objects.generate_url_cache()

        self.assertEqual('/', cache_url(1))
        self.assertEqual('/page-2/', cache_url(2))
        self.assertEqual('/page-1/page-3/', cache_url(3))

    def test_clear_url_cache(self):
        cache = get_cache('default')
        cache_url = lambda id: cache.get('ostinato:pages:page:%s:url' % id)

        Page.objects.generate_url_cache()  # Make sure there is a cache
        Page.objects.clear_url_cache()

        self.assertEqual(None, cache_url(1))
        self.assertEqual(None, cache_url(2))
        self.assertEqual(None, cache_url(3))


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
        p = Page.objects.create(
            title='Test Page', slug='test-page', template='pages.otherpage')
        self.assertEqual('pages/other_page.html', p.get_template())

    def test_add_content(self):
        create_pages()
        p = Page.objects.get(slug='page-1')
        p.contents.add_content(something='Some Content')
        self.assertEqual('Some Content', p.contents.something)

    def test_add_content_raises_exception_if_exists(self):
        create_pages()
        p = Page.objects.get(slug='page-1')
        p.contents.add_content(something='Some Content')

        with self.assertRaises(ContentError) as cm:
            p.contents.add_content(something='This should raise exception')

        e = cm.exception
        self.assertEqual(
            'Cannot add "something" to LandingPage object since that attribute already exists.',
            str(e))

    def test_inline_content_for_page(self):
        create_pages()
        p = Page.objects.get(slug='page-3')
        Contributor.objects.create(page=p, name='Contributor 1')
        qs = Contributor.objects.filter(page=p)
        self.assertEqual(qs[0], p.testing.all()[0])


class PageViewTestCase(TestCase):

    urls = 'ostinato.pages.urls'

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
        self.assertEqual(
            'pages/tests/landing_page.html', response.templates[0].name)

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

    def test_author_can_access_own_private_page(self):
        # First we make the page private
        p = Page.objects.get(slug='page-1')
        p.state = 1
        p.save()

        u = User.objects.get(username='user1')
        u.set_password('secret')
        u.save()

        self.client.login(username="user1", password='secret')
        response = self.client.get('/page-1/')
        self.assertEqual(200, response.status_code)

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


class ViewDispatcherTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def setUp(self):
        create_pages()

    def test_dispatcher_exists(self):
        page_dispatch

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

    def test_navbar_renders(self):
        t = Template('{% load pages_tags %}{% navbar %}')
        self.response = SimpleTemplateResponse(t)
        self.response.render()
        self.assertTrue(self.response.is_rendered)


class GetPageTemplateTagTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def test_tag_returns_page(self):
        create_pages()
        p = get_page(slug="page-1")
        self.assertEqual("Page 1", p.title)

    def test_tag_renders(self):
        t = Template('{% load pages_tags %}{% get_page slug="page-1" as somepage %}{{ somepage.title }}')
        response = SimpleTemplateResponse(t)
        response.render()
        self.assertTrue(response.is_rendered)


class FilterPageTemplateTagTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def test_tag_returns_queryset(self):
        create_pages()
        pages = filter_pages(template='pages.basicpage')
        self.assertEqual(2, len(pages))

    def test_tag_renders(self):
        t = Template('{% load pages_tags %}{% get_page template="pages.basicpage" as page_list %}')
        response = SimpleTemplateResponse(t)
        response.render()
        self.assertTrue(response.is_rendered)


class BreadCrumbsTempalteTagTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def test_tag_returns_breadcrumbs_for_page_in_context(self):
        create_pages()
        c = Context({"page": Page.objects.get(slug="page-3")})
        crumbs = breadcrumbs(c)

        expected_crumbs = [{
            'slug': u'page-1',
            'title': u'Page 1',
            'url': '/',
        }, {
            'slug': u'page-3',
            'title': u'Page 3',
            'url': '/page-1/page-3/',
        }]

        self.assertEqual(expected_crumbs, crumbs["breadcrumbs"])

    def test_tag_returns_breadcrumbs_for_page_argument(self):
        create_pages()
        c = Context({})
        crumbs = breadcrumbs(c, for_page=Page.objects.get(slug="page-3"))

        expected_crumbs = [{
            'slug': u'page-1',
            'title': u'Page 1',
            'url': '/',
        }, {
            'slug': u'page-3',
            'title': u'Page 3',
            'url': '/page-1/page-3/',
        }]

        self.assertEqual(expected_crumbs, crumbs['breadcrumbs'])

    def test_crumbs_can_have_custom_object(self):
        create_pages()
        c = Context({"page": Page.objects.get(slug="page-3")})

        # We will just use a page as the custom object. It doesn't really
        # matter, as long as the final object has a ``title`` and
        # ``get_absolute_url()``
        obj_page = Page.objects.get(id=1)
        crumbs = breadcrumbs(c, obj=obj_page)

        expected_crumbs = [{
            'slug': u'page-1',
            'title': u'Page 1',
            'url': '/',
        }, {
            'slug': u'page-3',
            'title': u'Page 3',
            'url': '/page-1/page-3/',
        }, {
            'title': u'Page 1',
            'url': u'/'
        }]

        self.assertEqual(expected_crumbs, crumbs['breadcrumbs'])

    def test_tag_renders(self):
        create_pages()
        t = Template('{% load pages_tags %}{% get_page slug="page-3" as page %}{% breadcrumbs %}')
        response = SimpleTemplateResponse(t)
        response.render()
        self.assertTrue(response.is_rendered)


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
            'node': 2,              # Move node id 2 ...
            'position': 'left',     # ... to the Left of ...
            'target': 1,            # ... node id 1
        }

        response = self.client.post('/page_reorder/', data)
        self.assertEqual(302, response.status_code)

        p = Page.objects.get(slug='page-1')
        p2 = Page.objects.get(slug='page-2')

        self.assertGreater(p.tree_id, p2.tree_id)
