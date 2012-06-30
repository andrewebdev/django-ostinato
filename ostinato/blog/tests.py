from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone

from ostinato.blog.models import BlogEntryBase
from ostinato.blog.workflow import BlogEntryWorkflow
from ostinato.blog.managers import BlogEntryManager


class Entry(BlogEntryBase):
    pass


def create_objects():
    u = User.objects.create(username='user1', password='',
        email='test@example.com')

    Entry.objects.create(
        title='Entry Title 1',
        slug='entry-title-1',
        content='Entry Content 1',
        author=u,
    )

    Entry.objects.create(
        title='Entry Title 2',
        slug='entry-title-2',
        content='Entry Content 2',
        author=u,
    )
    
    Entry.objects.create(
        title='Entry Title 3',
        slug='entry-title-3',
        content='Entry Content 3',
        author=u,
    )


class BlogEntryBaseTestCase(TestCase):

    def test_model_exists(self):
        BlogEntryBase

    def test_model_is_abstract(self):
        self.assertTrue(BlogEntryBase._meta.abstract)

    def test_model_instance(self):
        u = User.objects.create(username='user1', password='',
            email='test@example.com')

        entry = Entry.objects.create(
            title='Entry Title 1',
            slug='entry-title-1',
            content='Entry Content 1',
            author=u,
        )

    def test_slug_is_unique(self):
        create_objects()
        with self.assertRaises(IntegrityError):
            Entry.objects.create(title='Invalid', slug='entry-title-1',
                author=User.objects.all()[0])

    def test_unicode_name(self):
        create_objects()
        self.assertEqual('Entry Title 1', str(Entry.objects.get(id=1)))


class BlogEntryWorkflowTestCase(TestCase):

    def setUp(self):
        create_objects()

    def test_workflow_exists(self):
        BlogEntryWorkflow

    def test_publish_action_method(self):
        entry = Entry.objects.get(id=1)
        sm = BlogEntryWorkflow(instance=entry)

        self.assertEqual('Private', sm.state)
        self.assertEqual(None, entry.publish_date)

        sm.take_action('publish')

        # Now the state should be updated ...
        self.assertEqual('Published', sm.state)

        # ... and the publish date should also be updated
        self.assertGreaterEqual(timezone.now(), entry.publish_date)

    def test_archive_action_method(self):
        entry = Entry.objects.get(id=1)
        entry.state = 5  # force the state for now
        entry.save()

        sm = BlogEntryWorkflow(instance=entry)

        self.assertTrue(entry.allow_comments)
        sm.take_action('archive')

        self.assertEqual('Archived', sm.state)
        self.assertFalse(entry.allow_comments)

    def test_retract_from_archived_can_reset_date(self):
        entry = Entry.objects.get(id=1)
        sm = BlogEntryWorkflow(instance=entry)
        sm.take_action('publish')

        sm.take_action('archive')
        self.assertEqual('Archived', sm.state)
        self.assertIsNotNone(entry.publish_date)

        sm.take_action('retract')
        self.assertEqual('Private', sm.state)
        self.assertIsNotNone(entry.publish_date)

        # Reset the state to archived
        sm.take_action('publish')
        sm.take_action('archive')

        # Now test with the reset feature
        sm.take_action('retract', reset_publish_date=True)
        self.assertEqual('Private', sm.state)
        self.assertIsNone(entry.publish_date)

    def test_retract_from_published_can_reset_date(self):
        entry = Entry.objects.get(id=1)
        sm = BlogEntryWorkflow(instance=entry)
        sm.take_action('publish')

        sm.take_action('retract')
        self.assertEqual('Private', sm.state)
        self.assertIsNotNone(entry.publish_date)

        sm.take_action('publish')
        # Now test with the reset feature
        sm.take_action('retract', reset_publish_date=True)
        self.assertEqual('Private', sm.state)
        self.assertIsNone(entry.publish_date)


class BlogEntryManagerTestCase(TestCase):

    def test_manager_exists(self):
        BlogEntryManager

    def test_public_returns_only_published(self):
        create_objects()

        self.assertEqual([], list(Entry.objects.published()))

        # We need some published items
        for item in Entry.objects.filter(id__in=[2, 3]):
            sm = BlogEntryWorkflow(instance=item)
            sm.take_action('publish')
            item.save()

        self.assertEqual([2, 3],
            list(Entry.objects.published().values_list('id', flat=True)))

