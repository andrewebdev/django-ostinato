from django.test import TestCase
from django.db import models

from ostinato.statemachine import State, StateMachine, InvalidTransition


# Create a test model to test the StateMachine with
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=20, null=True, blank=True)
    state_num = models.IntegerField(null=True, blank=True)
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

    def test_get_choices(self):
        self.assertIn(('private', 'Private'), TestStateMachine.get_choices())
        self.assertIn(('public', 'Public'), TestStateMachine.get_choices())

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

    def test_get_available_actions(self):
        temp = TestModel.objects.create(name='Test Model 1', state='private')
        sm = TestStateMachine(instance=temp, state_field='other_state')

        self.assertEqual(['publish'], sm.actions)


    def test_override_state(self):
        temp = TestModel.objects.create(name='Test Model 1', state='private')
        sm = TestStateMachine(instance=temp, state='Test State Override')

        self.assertEqual('Test State Override', sm._state)


    def test_get_action_target(self):
        temp = TestModel.objects.create(name='Test Model 1', state='private')
        sm = TestStateMachine(instance=temp, state='private')

        self.assertEqual('public', sm.action_result('publish'))


    def test_get_permissions(self):
        perms = TestStateMachine.get_permissions()
        expected_perms = (
            ('private_view', '[Private] Can View'),
            ('private_edit', '[Private] Can Edit'),
            ('private_delete', '[Private] Can Delete'),

            ('public_view', '[Public] Can View'),
            ('public_edit', '[Public] Can Edit'),
            ('public_delete', '[Public] Can Delete'),

            ('can_publish', 'Can Publish'),
            ('can_retract', 'Can Retract'),
        )
        
        for p in expected_perms:
            self.assertIn(p, perms)


# Create some states and a StateMachine
class IntPrivate(State):
    verbose_name = 'Private'
    transitions = {'publish': 2}

    def publish(self):
        if self.instance:
            self.instance.message = 'Object made public'


class IntPublic(State):
    verbose_name = 'Public'
    transitions = {'retract': 1}

    def retract(self):
        if self.instance:
            self.instance.message = 'Object made private'


class TestIntegerStateMachine(StateMachine):
    state_map = {1: IntPrivate, 2: IntPublic}
    initial_state = 1 


class NumberedStateMachineTestCase(TestCase):

    def test_create_statemachine(self):
        sm = TestIntegerStateMachine()
        self.assertEqual(1, sm._state)
        self.assertEqual('Private', sm.state)

    def test_perform_action(self):
        sm = TestIntegerStateMachine()
        sm.take_action('publish')

        self.assertEqual(2, sm._state)
        self.assertEqual('Public', sm.state)

    def test_get_choices(self):
        self.assertEqual(
            ((1, 'Private'), (2, 'Public')),
            TestIntegerStateMachine.get_choices()
        )

    def test_get_permissions(self):
        expected_perms = (
            ('intprivate_view', '[IntPrivate] Can View'),
            ('intprivate_edit', '[IntPrivate] Can Edit'),
            ('intprivate_delete', '[IntPrivate] Can Delete'),
            ('can_publish', 'Can Publish'),

            ('intpublic_view', '[IntPublic] Can View'),
            ('intpublic_edit', '[IntPublic] Can Edit'),
            ('intpublic_delete', '[IntPublic] Can Delete'),
            ('can_retract', 'Can Retract'),
        )

        for p in expected_perms:
            self.assertIn(p, TestIntegerStateMachine.get_permissions())

    def test_get_available_actions(self):
        temp = TestModel.objects.create(name='Test Model 1', state_num=1)
        sm = TestIntegerStateMachine(instance=temp, state_field='state_num')

        self.assertEqual(['publish'], sm.actions)

    def test_with_instance(self):
        temp = TestModel.objects.create(name='Test Model 1', state_num=1)
        sm = TestIntegerStateMachine(instance=temp, state_field='state_num')

        sm.take_action('publish')
        temp.save()

        self.assertEqual(2, temp.state_num)
        self.assertEqual('Object made public', temp.message)

