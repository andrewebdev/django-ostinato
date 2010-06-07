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

    def testBase(self):
        self.assertequals(1, 2)

class ContentItemTestCase(CMSTestCase):
    def testItem(self):
        self.assertEquals(
            ContentItem.objects.all().len(),
            1
        )
