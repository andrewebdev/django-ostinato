from django.test import TestCase
from django.template import Context

from ostinato.pages.models import Page
from ostinato.pages.templatetags.pages_tags import (
    get_page,
    filter_pages,
    breadcrumbs,
)

from .utils import create_pages


class GetPageTemplateTagTestCase(TestCase):

    urls = 'ostinato.pages.urls'

    def test_tag_returns_page(self):
        create_pages()
        p = get_page(slug="page-1")
        self.assertEqual("Page 1", p.title)


class FilterPageTemplateTagTestCase(TestCase):

    def test_tag_returns_queryset(self):
        create_pages()
        pages = filter_pages(template='pages.basicpage')
        self.assertEqual(2, len(pages))


class BreadCrumbsTempalteTagTestCase(TestCase):

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
            'url': '/page-1/page-3',
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
            'url': '/page-1/page-3',
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
            'url': '/page-1/page-3',
        }, {
            'title': u'Page 1',
            'url': u'/'
        }]

        self.assertEqual(expected_crumbs, crumbs['breadcrumbs'])
