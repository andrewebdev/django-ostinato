from django.test import TestCase
from django.db import models

from ostinato.statemachine import State, StateMachine
from ostinato.statemachine import (
    InvalidState,
    InvalidTransition,
    InvalidStateMachine)

from ..workflow import *
from ..models import TestModel


class StateTestCase(TestCase):

    def test_class_exists(self):
        State

    def test_init_and_kwargs(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(
            instance=temp,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertEqual(temp, private.instance)
        self.assertIn('arg1', private.extra_args)
        self.assertIn('arg2', private.extra_args)

    def test_set_state(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(
            instance=temp,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertEqual('test_state', private.set_state('test_state'))
        self.assertEqual('test_state', temp.state)

    def test_transition(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(
            instance=temp,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertEqual('public', private.transition('publish'))

    def test_invalid_transition(self):
        temp = TestModel(name='Test Model 1', state='private')
        private = Private(
            instance=temp,
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
        perms = TestStateMachine.get_permissions('testmodel')
        expected_perms = (
            ('private_view_testmodel', '[Private] Can View testmodel'),
            ('private_edit_testmodel', '[Private] Can Edit testmodel'),
            ('private_delete_testmodel', '[Private] Can Delete testmodel'),

            ('public_view_testmodel', '[Public] Can View testmodel'),
            ('public_edit_testmodel', '[Public] Can Edit testmodel'),
            ('public_delete_testmodel', '[Public] Can Delete testmodel'),

            ('can_publish_testmodel', 'Can Publish testmodel'),
            ('can_retract_testmodel', 'Can Retract testmodel'),
        )

        for p in expected_perms:
            self.assertIn(p, perms)

    def test_verify_statemachine(self):
        temp = TestModel.objects.create(name='Test Model 1', state='invalid')

        re = """"invalid" is not a valid state for InvalidSM. Valid states are \\['public', 'private', 'error'\\]"""
        with self.assertRaisesRegexp(InvalidStateMachine, re):
            InvalidSM(instance=temp)

        re = "ErrorState contains an invalid action target, invalid."
        with self.assertRaisesRegexp(InvalidState, re):
            ErrorSM(instance=temp)


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
            ('intprivate_view_testmodel', '[Private] Can View Test'),
            ('intprivate_edit_testmodel', '[Private] Can Edit Test'),
            ('intprivate_delete_testmodel', '[Private] Can Delete Test'),
            ('can_publish_testmodel', 'Can Publish Test'),

            ('intpublic_view_testmodel', '[Public] Can View Test'),
            ('intpublic_edit_testmodel', '[Public] Can Edit Test'),
            ('intpublic_delete_testmodel', '[Public] Can Delete Test'),
            ('can_retract_testmodel', 'Can Retract Test'),
        )

        for p in expected_perms:
            self.assertIn(p, TestIntegerStateMachine.get_permissions(
                'testmodel', verbose_prefix='Test'))

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

