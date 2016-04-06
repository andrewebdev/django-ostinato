from django.test import TestCase
from django.utils import timezone

from ostinato.blog.workflow import BlogEntryWorkflow

from ..models import Entry
from .utils import create_objects


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

    def test_approve_from_review_sets_publish_date(self):
        entry = Entry.objects.get(id=1)
        sm = BlogEntryWorkflow(instance=entry)

        sm.take_action('review')
        self.assertEqual('Review', sm.state)
        self.assertIsNone(entry.publish_date)

        sm.take_action('approve')
        self.assertEqual('Published', sm.state)
        self.assertIsNotNone(entry.publish_date)

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
