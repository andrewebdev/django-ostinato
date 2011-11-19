from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from ostinato.models import ContentItem
from ostinato._statemachine.models import StateMachineBase, DefaultStateMachine
from ostinato._statemachine.models import InvalidAction
from ostinato._statemachine.models import sm_pre_action, sm_post_action


class StateMachineBaseModelTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json']

    def setUp(self):
        self.content_item_type = ContentType.objects.get(
            app_label='ostinato', model='contentitem')

        self.sm = StateMachineBase(
            state='private',
            content_type=self.content_item_type,
            object_id=1,
        )
        
    def test_model_exists(self):
        pass

    def test_model_is_abstract(self):
        self.assertTrue(StateMachineBase._meta.abstract)

    def test_generic_relation_exists(self):
        expected_item = ContentItem.objects.get(id=1)
        self.assertEqual(expected_item, self.sm.content_object)

    def test_generic_relation_unique_together(self):
        self.assertEqual((('content_type', 'object_id'),),
            StateMachineBase._meta.unique_together)

    def test_unicode(self):
        self.assertEqual('content item, 1 (private)', self.sm.__unicode__())


class DefaultStateMachineTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json']

    def setUp(self):
        self.content_item_type = ContentType.objects.get(
            app_label='ostinato', model='contentitem')

        self.sm = DefaultStateMachine.objects.create(
            state='private', content_type=self.content_item_type, object_id=1)
        self.sm.save()

    def test_default_statemachine_exists(self):
        pass  # This is basically done in setUp()

    def test_statemachine_permissions(self):
        expected_permissions = (
            ('can_submit', 'Can submit for review'),
            ('can_reject', 'Can reject'),
            ('can_publish', 'Can publish'),
            ('can_retract', 'Can retract'),
            ('can_archive', 'Can archive'),
        )
        self.assertEqual(expected_permissions,
            DefaultStateMachine._meta.permissions)

    def test_statemachine(self):
        state_actions = {
            'private': ('can_submit', 'can_publish'),
            'review': ('can_publish', 'can_reject'),
            'published': ('can_retract', 'can_archive'),
            'archived': ('can_retract',),
        }
        self.assertEqual(state_actions,
            DefaultStateMachine.SMOptions.state_actions)

    def test_action_targets(self):
        action_targets = {
            'can_submit': 'review',
            'can_reject': 'private',
            'can_publish': 'published',
            'can_retract': 'private',
            'can_archive': 'archived',
        }
        self.assertEqual(action_targets,
            DefaultStateMachine.SMOptions.action_targets)

    def test_statemachine_available_actions(self):
        available_actions = ('can_submit', 'can_publish')
        self.assertEqual(available_actions, self.sm.get_actions())

    def test_statemachine_take_action(self):
        self.sm.state = 'private'
        self.sm.save()
        self.sm.take_action('can_publish')
        self.assertEqual('published', self.sm.state)

    def test_invalid_action(self):
        with self.assertRaises(InvalidAction):
            self.sm.take_action('invalid')


class StateMachineSignalsTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json']

    def setUp(self):
        self.content_item_type = ContentType.objects.get(
            app_label='ostinato', model='contentitem')

        self.sm = DefaultStateMachine.objects.create(
            state='private', content_type=self.content_item_type, object_id=1)
        self.sm.save()

    def test_pre_action_signal(self):

        signal_resp = {}
        expected_resp = {
            'action': 'can_submit',
            'instance': self.sm
        }

        def signal_listner(sender, instance, **kwargs):
            signal_resp.update({
                'action': kwargs['action'], 'instance': instance})

        # Connect and send
        sm_pre_action.connect(signal_listner, sender=self.sm)
        self.sm.take_action('can_submit')

        self.assertEqual(expected_resp, signal_resp)

    def test_post_action_signal(self):
        
        signal_resp = {}
        expected_resp = {
            'action': 'can_publish',
            'instance': self.sm,
            'new_state': 'published'
        }

        def signal_listner(sender, instance, **kwargs):
            signal_resp.update({
                'action': kwargs['action'], 'instance': instance,
                'new_state': instance.state
            })

        sm_post_action.connect(signal_listner, sender=self.sm)
        self.sm.take_action('can_publish')
        self.assertEqual(expected_resp, signal_resp)
