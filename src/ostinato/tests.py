from django.test import TestCase
from django.test.client import RequestFactory
from django.template import Template, Context
from django.template.response import SimpleTemplateResponse

from ostinato.models import ContentItem, BasicPage
from ostinato.core import OstinatoCMS, register_apps


class CMSTestCase(TestCase):

    def test_register_and_unregister_model(self):
        self.assertEquals(0, ContentItem.objects.all().count())
        OstinatoCMS.register(BasicPage)

        page = BasicPage(title="BasicPage 1", content="BasicPage 1 Content")
        page.save()
        self.assertEquals(1, ContentItem.objects.all().count())

        OstinatoCMS.unregister(BasicPage) ## Need this for some cleanup
        page2 = BasicPage(title="BasicPage 2", content="BasicPage 2 Content")
        self.assertEquals(1, ContentItem.objects.all().count())

    def test_register_apps(self):
        register_apps()

        self.assertEquals(0, ContentItem.objects.all().count())

        page = BasicPage(title="page1", content="page 1 content")
        page.save()
        self.assertEquals(1, ContentItem.objects.all().count())

        OstinatoCMS.unregister(BasicPage) ## Need this for some cleanup


class StateMachineTestCase(TestCase):

    def setUp(self):
        OstinatoCMS.register(BasicPage)
        page1 = BasicPage.objects.create(
            title="BasicPage 1", content="Basic Page 1 Content")
        OstinatoCMS.unregister(BasicPage)

        self.content_item = ContentItem.objects.all()[0]

    def test_content_item_default_state(self):
        self.assertEqual('Private', self.content_item.sm_state)

    def test_statemachine_take_action(self):
        self.content_item.sm_take_action('Submit')
        self.assertEqual('Review', self.content_item.sm_state)

    def test_publish_date_changed_after_publish_action(self):
        self.assertEqual(None, self.content_item.publish_date)
        self.content_item.sm_take_action('Publish')
        self.assertNotEqual(None, self.content_item.publish_date)


class ContentItemTestCase(TestCase):

    urls = 'ostinato.urls'

    def setUp(self):
        OstinatoCMS.register(BasicPage)

        page1 = BasicPage.objects.create(
            title="BasicPage 1", content="Basic Page 1 Content")
        page2 = BasicPage.objects.create(
            title="BasicPage 2", content="Basic Page 2 Content")
        page3 = BasicPage.objects.create(
            title="BasicPage 3", content="Basic Page 3 Content")

        self.content_item = ContentItem.objects.all()[0]
        self.content_item2 = ContentItem.objects.all()[1]
        self.content_item3 = ContentItem.objects.all()[2]
        self.content_item2.parent = self.content_item
        self.content_item2.save()
        self.content_item3.parent = self.content_item2
        self.content_item3.save()

    def test_content_item_prepopulated_fields(self):
        """
        Some of the fields in the content item are guessed and prepopulated
        from the registered model. Check this here.
        """
        self.assertEqual('BasicPage 1', self.content_item.title)
        self.assertEqual('basicpage-1', self.content_item.slug)

    def test_get_parents(self):
        parent_list = [p for p in self.content_item3._get_parents()]
        expected_parents = [self.content_item, self.content_item2]
        self.assertEqual(expected_parents, parent_list)

    def test_get_absolute_url(self):
        self.assertEqual('/basicpage-1/', self.content_item.get_absolute_url())

    def test_homepage_url(self):
        homepage = BasicPage.objects.create(title='HomePage', content='Homepage')
        homeitem = ContentItem.objects.get_for(homepage)
        self.assertEqual('/', homeitem.get_absolute_url())

    def test_get_edit_url(self):
        self.assertEqual('/edit/basicpage-1/', self.content_item.get_edit_url())

    def test_nested_pages_urls(self):
        self.assertEqual(
            '/basicpage-1/basicpage-2/', self.content_item2.get_absolute_url())

    def test_deep_nested_pages_urls(self):
        self.assertEqual('/basicpage-1/basicpage-2/basicpage-3/',
            self.content_item3.get_absolute_url())


class ContentItemManagerTestCase(TestCase):

    urls = 'ostinato.urls'

    def setUp(self):
        OstinatoCMS.register(BasicPage)

        page1 = BasicPage.objects.create(
            title="BasicPage 1", content="Basic Page 1 Content")
        page2 = BasicPage.objects.create(
            title="BasicPage 2", content="Basic Page 2 Content")
        page3 = BasicPage.objects.create(
            title="BasicPage 3", content="Basic Page 3 Content")

        self.content_item1 = ContentItem.objects.all()[0]
        self.content_item2 = ContentItem.objects.all()[1]
        self.content_item3 = ContentItem.objects.all()[2]

        self.content_item2.parent = self.content_item1
        self.content_item2.save()

        self.content_item3.parent = self.content_item2
        self.content_item3.save()

    def test_correct_parents(self):
        self.assertEqual(self.content_item1, self.content_item2.parent)
        self.assertEqual(self.content_item2, self.content_item3.parent)

    def test_get_for(self):
        page = BasicPage.objects.get(id=1)
        self.assertEqual(self.content_item1, ContentItem.objects.get_for(page))

    def test_get_parents(self):
        parents = [p for p in ContentItem.objects._get_parents(self.content_item3)]
        expected_parents = [self.content_item1, self.content_item2]
        self.assertEqual(expected_parents, parents)

    def test_get_empty_navbar(self):
        empty_nav = ContentItem.objects.get_navbar()
        self.assertEqual([], empty_nav)

    def test_basic_navbar(self):
        page4 = BasicPage.objects.create(
            title='BasicPage 4', content='BasicPage 4 Content')
        ContentItem.objects.all().update(show_in_nav=True)
        expected_nav = [{
            'title': u'BasicPage 1',
            'url': '/basicpage-1/',
        },
        {
            'title': u'BasicPage 4',
            'url': '/basicpage-4/',
        }]
        self.assertEqual(expected_nav, ContentItem.objects.get_navbar())

    def test_navbar_with_parent(self):
        ContentItem.objects.all().update(show_in_nav=True)
        expected_nav = [{
            'title': u'BasicPage 2',
            'url': '/basicpage-1/basicpage-2/',
        }]
        self.assertEqual(expected_nav,
            ContentItem.objects.get_navbar(self.content_item1))

    def test_get_breadcrumbs(self):
        expected_crumbs = [{
            'title': u'BasicPage 1',
            'url': '/basicpage-1/',
            'current': False
        },
        {
            'title': u'BasicPage 2',
            'url': '/basicpage-1/basicpage-2/',
            'current': False
        },
        {
            'title': u'BasicPage 3',
            'url': '/basicpage-1/basicpage-2/basicpage-3/',
            'current': True
        }]
        crumbs = ContentItem.objects.get_breadcrumbs_for(self.content_item3)
        self.assertEqual(expected_crumbs, crumbs)


class OstinatoContentModifiersTestCase(TestCase):

    def test_register_modifier(self):
        pass

    def test_modifier_tag_single(self):
        pass

    def test_modifier_tag_multiple(self):
        pass

    def test_modifier_exclude(self):
        pass
