from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User

from ostinato.blog.models import BlogEntryBase

from ..models import Entry

from .utils import create_objects


class BlogEntryBaseTestCase(TestCase):

    def test_model_exists(self):
        BlogEntryBase

    def test_model_is_abstract(self):
        self.assertTrue(BlogEntryBase._meta.abstract)

    def test_model_instance(self):
        u = User.objects.create(
            username='user1', password='', email='test@example.com')

        Entry.objects.create(
            title='Entry Title 1',
            slug='entry-title-1',
            content='Entry Content 1',
            author=u,
        )

    def test_slug_is_unique(self):
        create_objects()
        with self.assertRaises(IntegrityError):
            Entry.objects.create(
                title='Invalid', slug='entry-title-1',
                author=User.objects.all()[0])

    def test_unicode_name(self):
        create_objects()
        self.assertEqual('Entry Title 1', str(Entry.objects.get(id=1)))

