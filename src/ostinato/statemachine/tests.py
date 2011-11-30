from django.test import TestCase
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.template import Context, Template
from django.template.response import SimpleTemplateResponse

from ostinato.models import ContentItem
from models import StateMachineBase, DefaultStateMachine, StateMachineField
from models import InvalidAction
from models import sm_pre_action, sm_post_action
from templatetags.statemachine_tags import GetStateMachineNode


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
            content_type=self.content_item_type, object_id=1)
        self.sm.save()

    def test_default_statemachine_exists(self):
        pass  # This is basically done in setUp()

    def test_initial_state(self):
        self.assertEqual('private', DefaultStateMachine.SMOptions.initial_state)
        self.assertEqual('private', self.sm.state)

    def test_statemachine_permissions(self):
        expected_permissions = (
            ('submit', 'Can submit for review'),
            ('reject', 'Can reject'),
            ('publish', 'Can publish'),
            ('retract', 'Can retract'),
            ('archive', 'Can archive'),
        )
        self.assertEqual(expected_permissions,
            DefaultStateMachine._meta.permissions)

    def test_statemachine(self):
        state_actions = {
            'private': ('submit', 'publish'),
            'review': ('publish', 'reject'),
            'published': ('retract', 'archive'),
            'archived': ('retract',),
        }
        self.assertEqual(state_actions,
            DefaultStateMachine.SMOptions.state_actions)

    def test_action_targets(self):
        action_targets = {
            'submit': 'review',
            'reject': 'private',
            'publish': 'published',
            'retract': 'private',
            'archive': 'archived',
        }
        self.assertEqual(action_targets,
            DefaultStateMachine.SMOptions.action_targets)

    def test_statemachine_available_actions(self):
        available_actions = ('submit', 'publish')
        self.assertEqual(available_actions, self.sm.get_actions())

    def test_statemachine_action_display(self):
        self.assertEqual('Can submit for review',
            self.sm.get_action_display('submit'))

    def test_statemachine_take_action(self):
        self.sm.state = 'private'
        self.sm.save()
        self.sm.take_action('publish')
        self.assertEqual('published', self.sm.state)

    def test_invalid_action(self):
        with self.assertRaises(InvalidAction):
            self.sm.take_action('invalid')

    def test_admin_permissions_exist(self):
        ct = ContentType.objects.get(app_label='statemachine',
            model='defaultstatemachine')

        perms = list(Permission.objects.filter(content_type=ct)\
            .values_list('codename', flat=True))

        ## Django returns this ordered by codename
        expected_perms = [
            u'add_defaultstatemachine',
            u'archive',
            u'change_defaultstatemachine',
            u'delete_defaultstatemachine',

            # These are our permissions
            u'publish',
            u'reject',
            u'retract',
            u'submit',
        ]

        self.assertListEqual(expected_perms, perms)


class StateMachineSignalsTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json']

    def setUp(self):
        self.content_item_type = ContentType.objects.get(
            app_label='ostinato', model='contentitem')

        self.sm = DefaultStateMachine.objects.create(
            state='private', content_type=self.content_item_type, object_id=1)
        self.sm.save()

    def test_pre_action_signal(self):

        def signal_listner(sender, **kwargs):
            sender.content_object.show_in_nav = True
            sender.content_object.save()

        # Connect and send
        sm_pre_action.connect(signal_listner)

        self.sm.take_action('submit')
        self.assertTrue(ContentItem.objects.get(id=1).show_in_nav)

    def test_post_action_signal(self):

        def signal_listner(sender, **kwargs):
            sender.content_object.show_in_nav = True
            sender.content_object.save()

        sm_post_action.connect(signal_listner)

        self.sm.take_action('publish')
        self.assertTrue(ContentItem.objects.get(id=1).show_in_nav)


class _DummyModel(models.Model):
    name = models.CharField(max_length=50)
    pre = models.BooleanField(default=False)
    post = models.BooleanField(default=False)
    statemachine = StateMachineField(DefaultStateMachine)


class StateMachineFieldTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json']

    def setUp(self):
        self.dummy = _DummyModel(name="Dummy 1")
        self.dummy.save()

    def test_statemachine_field_exists(self):
        field = StateMachineField(DefaultStateMachine)

    def test_can_get_statemachine_from_field(self):
        self.assertEqual('private', self.dummy.statemachine.state)

    def test_can_take_actions(self):
        self.dummy.statemachine.take_action('publish')
        self.assertEqual('published', self.dummy.statemachine.state)


class StateMachineManagerTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json']

    def test_get_statemachine(self):
        sm = DefaultStateMachine.objects.get_statemachine(
            ContentItem.objects.get(id=1))
        self.assertEqual(1, DefaultStateMachine.objects.all().count())


class GetStateMachineTemplateTagTestCase(TestCase):

    fixtures = ['ostinato_test_fixtures.json']

    def test_template_tag_renders(self):
        template = Template('{% load statemachine_tags %}{% get_statemachine statemachine.defaultstatemachine for item %}{{ statemachine.state }}')
        context = Context({'item': ContentItem.objects.get(id=1)})
        response = template.render(context) 
        self.assertEqual('private', response)
