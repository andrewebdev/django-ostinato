from django.test import TestCase
from django.contrib.flatpages.models import FlatPage

from ostinato.models import ContentItem

class CMSTestCase(TestCase):
    def setUp(self):
        self.item = ContentItem.objects.create(
            title="Home",
            description="A short description of the content",
            location="/",
        )

        self.item2 = ContentItem.objects.create(
            title="Item2",
            short_title="Test",
            description="A second test item",
            location="/test/",
            parent=self.item,
        )

class ContentItemTestCase(CMSTestCase):
    def testItem(self):
        self.assertEquals(ContentItem.objects.all().count(), 2)

    def testStatus(self):
        self.assertEquals(self.item.status, self.item.DRAFT,
            "Incorrect status (%s) for item." % self.item.status)
        self.assertEquals(self.item.publish_date, None)
        self.item.action_publish()
        self.assertEquals(self.item.status, self.item.PUBLISHED,
            "Incorrect status (%s) for item after action_publish()" % self.item.status)
        self.failUnless(self.item.publish_date != None,
            "Publish Date should not be none")

    def testURL(self):
        self.assertEquals(self.item.get_absolute_url(), '/')

    def testNavBar(self):
        nav_menu = ContentItem.objects.get_nav_bar()
        self.assertEquals(
            nav_menu,
            [{'title': 'Home', 'url': '/'}],
        )
        sub_menu = ContentItem.objects.get_nav_bar(parent=self.item)
        self.assertEquals(
            sub_menu,
            [{'title': 'Test', 'url': '/test/'}],
        )

    def testBreadCrumbs(self):
        crumbs = ContentItem.objects.get_breadcrumbs(self.item)
        self.assertEquals(
            crumbs,
            [{'title': 'Home', 'url': '/', 'current': True}]
        )

        crumbs = ContentItem.objects.get_breadcrumbs(self.item2)
        self.assertEquals(
            crumbs,
            [
                {'title': 'Home', 'url': '/', 'current': False},
                {'title': 'Test', 'url': '/test/', 'current': True}
            ]
        )
