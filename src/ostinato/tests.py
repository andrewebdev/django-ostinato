from django.test import TestCase
from django.contrib.flatpages.models import FlatPage

from ostinato.models import ContentItem

class CMSTestCase(TestCase):
    def setUp(self):
        # Create some basic test content
        self.homepage = FlatPage.objects.create(
            url="/",
            title="Home",
            content="Lorem Ipsum dolor set..."
        )
        self.aboutus = FlatPage.objects.create(
            url="/about-us/",
            title="About Us",
            content="Lorem Ipsum dolor set..."
        )
        self.contact = FlatPage.objects.create(
            url="/contact/",
            title="Contact Us",
            content="Lorem Ipsum dolor set..."
        )

        # Define a standard ContentItem
        self.os_homepage = ContentItem.objects.create(
            title="Home",
            description="The Home Page",
            location="/",
        )
        # Define a ContentItem with a parent and custom location
        self.os_aboutus = ContentItem.objects.create(
            title="About Us",
            short_title="About",
            description="About Us Page",
            location="/about-us/",
            parent=self.os_homepage,
        )
        # Define a ContentItem with a parent and pointing to another
        # django app
        self.os_contact = ContentItem.objects.create(
            title="Contact Us",
            short_title="Contact",
            description="Contact us page",
            location="/contact/",
            parent=self.os_homepage,
        )

class ContentItemTestCase(CMSTestCase):
    # def testStatus(self):
    #     self.assertEquals(self.item.status, self.item.DRAFT,
    #         "Incorrect status (%s) for item." % self.item.status)
    #     self.assertEquals(self.item.publish_date, None)
    #     self.item.action_publish()
    #     self.assertEquals(self.item.status, self.item.PUBLISHED,
    #         "Incorrect status (%s) for item after action_publish()" % self.item.status)
    #     self.failUnless(self.item.publish_date != None,
    #         "Publish Date should not be none")

    # def testURL(self):
    #     self.assertEquals(self.item.get_absolute_url(), '/')

    def testNavBar(self):
        root = ContentItem.objects.get_navbar()
        self.assertEquals(
            root,
            [{'title': 'Home', 'url': '/'}],
        )
        sub = ContentItem.objects.get_navbar(parent=self.os_homepage)
        self.assertEquals(
            sub,
            [{'title': 'About', 'url': '/about-us/'},
             {'title': 'Contact', 'url': '/contact/'}],
        )

    def testBreadCrumbs(self):
        crumbs = ContentItem.objects.get_breadcrumbs(self.os_aboutus)
        self.assertEquals(
            crumbs,
            [{'title': 'Home', 'url': '/', 'current': False},
             {'title': 'About', 'url': '/about-us/',
              'current': True}
            ]
        )

## Doctests are nice for documentation :)
__test__ = {
"doctest": """

"""}
