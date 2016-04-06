from django.test import TestCase

from ostinato.blog.managers import BlogEntryManager

from ..models import Entry
from .utils import create_objects


class BlogEntryManagerTestCase(TestCase):

    def test_manager_exists(self):
        BlogEntryManager

    def test_public_returns_only_published(self):
        create_objects()
        self.assertEqual([], list(Entry.objects.published()))
        # We need some published items
        Entry.objects.filter(id__in=[2, 3]).update(state=5)
        self.assertEqual(
            [3, 2],
            list(Entry.objects.published().values_list('id', flat=True)))

