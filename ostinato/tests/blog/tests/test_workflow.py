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

        self.assertEqual('private', sm.state.value)
        self.assertEqual(None, entry.publish_date)

        sm.transition('publish')

        # Now the state should be updated ...
        self.assertEqual('published', sm.state.value)

        # ... and the publish date should also be updated
        self.assertGreaterEqual(timezone.now(), entry.publish_date)

    def test_approve_from_review_sets_publish_date(self):
        entry = Entry.objects.get(id=1)
        sm = BlogEntryWorkflow(instance=entry)

        sm.transition('review')
        self.assertEqual('review', sm.state.value)
        self.assertIsNone(entry.publish_date)

        sm.transition('approve')
        self.assertEqual('published', sm.state.value)
        self.assertIsNotNone(entry.publish_date)

    def test_archive_action_method(self):
        entry = Entry.objects.get(id=1)
        entry.state = 'published'
        entry.save()

        sm = BlogEntryWorkflow(instance=entry)

        self.assertTrue(entry.allow_comments)
        sm.transition('archive')

        self.assertEqual('archived', sm.state.value)
        self.assertFalse(entry.allow_comments)

    def test_retract_from_archived_can_reset_date(self):
        entry = Entry.objects.get(id=1)
        sm = BlogEntryWorkflow(instance=entry)
        sm.transition('publish')

        sm.transition('archive')
        self.assertEqual('archived', sm.state.value)
        self.assertIsNotNone(entry.publish_date)

        sm.transition('retract')
        self.assertEqual('private', sm.state.value)
        self.assertIsNotNone(entry.publish_date)

        # Reset the state to archived
        sm.transition('publish')
        sm.transition('archive')

        # Now test with the reset feature
        sm.transition('retract', reset_publish_date=True)
        self.assertEqual('private', sm.state.value)
        self.assertIsNone(entry.publish_date)

    def test_retract_from_published_can_reset_date(self):
        entry = Entry.objects.get(id=1)
        sm = BlogEntryWorkflow(instance=entry)
        sm.transition('publish')

        sm.transition('retract')
        self.assertEqual('private', sm.state.value)
        self.assertIsNotNone(entry.publish_date)

        sm.transition('publish')
        # Now test with the reset feature
        sm.transition('retract', reset_publish_date=True)
        self.assertEqual('private', sm.state.value)
        self.assertIsNone(entry.publish_date)
