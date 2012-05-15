from django.test import TestCase
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.template import Context, Template
from django.template.response import SimpleTemplateResponse

from ostinato.statemachine.models import (StateMachineBase, DefaultStateMachine,
    StateMachineField)
from ostinato.statemachine.models import InvalidAction
from ostinato.statemachine.models import sm_pre_action, sm_post_action
from ostinato.statemachine.templatetags.statemachine_tags import GetStateMachineNode


class ContentItem(models.Model):
    name = models.CharField(max_length=50)
    pre = models.BooleanField(default=False)
    post = models.BooleanField(default=False)
    statemachine = StateMachineField(DefaultStateMachine)


class _SetupMixin(object):

    def setUp(self):
        ContentItem.objects.create(name='Content Item 1')
        ContentItem.objects.create(name='Content Item 2')
        ContentItem.objects.create(name='Content Item 3')


class StateMachineBaseModelTestCase(_SetupMixin, TestCase):

    def setUp(self):
        self.content_item_type = ContentType.objects.get(
            app_label='statemachine', model='contentitem')

        self.sm = StateMachineBase(
            state='private',
            content_type=self.content_item_type,
            object_id=1,
        )
        super(StateMachineBaseModelTestCase, self).setUp()

        
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


class DefaultStateMachineTestCase(_SetupMixin, TestCase):

    def setUp(self):
        super(DefaultStateMachineTestCase, self).setUp()

        self.content_item_type = ContentType.objects.get(
            app_label='statemachine', model='contentitem')

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
            ('submit', 'Submit for review'),
            ('reject', 'Reject'),
            ('publish', 'Publish'),
            ('retract', 'Retract'),
            ('archive', 'Archive'),
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
        self.assertEqual('Submit for review',
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


class StateMachineSignalsTestCase(_SetupMixin, TestCase):

    def setUp(self):
        super(StateMachineSignalsTestCase, self).setUp()

        self.content_item_type = ContentType.objects.get(
            app_label='statemachine', model='contentitem')

        self.sm = DefaultStateMachine.objects.create(
            state='private', content_type=self.content_item_type, object_id=1)
        self.sm.save()

    def test_pre_action_signal(self):

        def signal_listner(sender, **kwargs):
            sender.content_object.pre = True
            sender.content_object.save()

        # Connect and send
        sm_pre_action.connect(signal_listner)

        self.sm.take_action('submit')
        self.assertTrue(ContentItem.objects.get(id=1).pre)
        self.assertFalse(ContentItem.objects.get(id=1).post)

    def test_post_action_signal(self):

        def signal_listner(sender, **kwargs):
            sender.content_object.post = True
            sender.content_object.save()

        sm_post_action.connect(signal_listner)

        self.sm.take_action('publish')
        self.assertTrue(ContentItem.objects.get(id=1).post)
        self.assertFalse(ContentItem.objects.get(id=1).pre)


class StateMachineFieldTestCase(_SetupMixin, TestCase):

    def test_statemachine_field_exists(self):
        field = StateMachineField(DefaultStateMachine)

    def test_can_get_statemachine_from_field(self):
        ci = ContentItem.objects.get(id=1)
        self.assertEqual('private', ci.statemachine.state)

    def test_can_take_actions(self):
        ci = ContentItem.objects.get(id=1)
        ci.statemachine.take_action('publish')
        self.assertEqual('published', ci.statemachine.state)


class StateMachineManagerTestCase(_SetupMixin, TestCase):

    def setUp(self):
        super(StateMachineManagerTestCase, self).setUp()

        ci = ContentItem.objects.get(id=1)
        ci.statemachine.take_action('publish')

    def test_get_statemachine(self):
        sm = DefaultStateMachine.objects.get_statemachine(
            ContentItem.objects.get(id=2))
        self.assertEqual(2, DefaultStateMachine.objects.all().count())

    def test_filter_has_state_returns_all(self):
        # Other than ci model, we want a seperate content object as well
        sm = DefaultStateMachine.objects.get_statemachine(
            ContentItem.objects.get(id=2))
        sm.take_action('publish')

        qs = DefaultStateMachine.objects.has_state('published')
        qs = list(qs.values_list('id', flat=True))
        self.assertEqual([1, 2], qs)

    def test_filter_has_state_with_extra_filter_args(self):
        # Other than cimodel, we want a seperate content object as well
        sm = DefaultStateMachine.objects.get_statemachine(
            ContentItem.objects.get(id=3))
        sm.take_action('publish')

        qs = DefaultStateMachine.objects.has_state('published',
            content_type__model='contentitem')
        qs = list(qs.values_list('id', flat=True))
        self.assertEqual([1, 2], qs)


class GetStateMachineTemplateTagTestCase(_SetupMixin, TestCase):

    def test_template_tag_renders(self):
        template = Template('{% load statemachine_tags %}{% get_statemachine statemachine.defaultstatemachine for item %}{{ statemachine.state }}')
        context = Context({'item': ContentItem.objects.get(id=1)})
        response = template.render(context) 
        self.assertEqual('private', response)


#### New Statemachine
from ostinato.statemachine.core import State, StateMachine, InvalidTransition

# Create a test model to test the StateMachine with
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=20, choices=(
        ('private', 'Private'),
        ('public', 'Public'),
    ))
    other_state = models.CharField(max_length=20, null=True, blank=True)
    message = models.CharField(max_length=250, null=True, blank=True)


# Create some states and a StateMachine
class Private(State):
    verbose_name = 'Private'
    transitions = {'publish': 'public'}

    def publish(self):
        if self.instance:
            self.instance.message = 'Object made public'


class Public(State):
    verbose_name = 'Public'
    transitions = {'retract': 'private'}

    def retract(self):
        if self.instance:
            self.instance.message = 'Object made private'


class TestStateMachine(StateMachine):
    state_map = {'private': Private, 'public': Public}
    initial_state = 'private'


# Now test the states and statemachine
class StateTestCase(TestCase):

    def test_class_exists(self):
        State

    def test_init_and_kwargs(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(instance=temp,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertEqual(temp, private.instance)
        self.assertIn('arg1', private.extra_args)
        self.assertIn('arg2', private.extra_args)

    def test_set_state(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(instance=temp,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertEqual('test_state', private.set_state('test_state'))
        self.assertEqual('test_state', temp.state)

    def test_transition(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(instance=temp,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertEqual('public', private.transition('publish'))

    def test_invalid_transition(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(instance=temp,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        with self.assertRaises(InvalidTransition):
            private.transition('invalid_action')


class StateMachineTestCase(TestCase):

    def test_class_exists(self):
        StateMachine

    def test_create_statemachine(self):
        sm = TestStateMachine()
        self.assertEqual('private', sm._state)

    def test_perform_action(self):
        sm = TestStateMachine()
        sm.take_action('publish')

        self.assertEqual('public', sm._state)

    def test_invalid_action(self):
        sm = TestStateMachine()

        with self.assertRaises(InvalidTransition):
            sm.take_action('retract')

    def test_with_instance(self):
        temp = TestModel.objects.create(name='Test Model 1', state='private')
        sm = TestStateMachine(instance=temp)

        sm.take_action('publish')
        temp.save()

        self.assertEqual('public', temp.state)
        self.assertEqual('Object made public', temp.message)

    def test_with_instance_custom_state_field(self):
        temp = TestModel.objects.create(name='Test Model 1', state='private')
        sm = TestStateMachine(instance=temp, state_field='other_state')

        sm.take_action('publish')
        temp.save()

        self.assertEqual('private', temp.state)
        self.assertEqual('public', temp.other_state)

