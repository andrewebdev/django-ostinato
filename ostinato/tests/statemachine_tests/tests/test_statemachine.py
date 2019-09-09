from django.test import TestCase

from ostinato.statemachine import State, StateMachine
from ostinato.statemachine import InvalidTransition

from ..workflow import Private, TestStateMachine, TestIntegerStateMachine
from ..models import TestModel


class MockManager(object):
    instance = TestModel(name='Test Model 1', state='private')

    def get_state_by_value(self, value):
        return 'test_state'


class StateTestCase(TestCase):

    def test_class_exists(self):
        State

    def test_init_and_kwargs(self):
        private = Private(
            manager=MockManager(),
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertIn('arg1', private.extra_args)
        self.assertIn('arg2', private.extra_args)

    def test_transition(self):
        manager = MockManager()
        private = Private(
            manager=manager,
            **{'arg1': 'Argument 1', 'arg2': 'Argument 2'})

        self.assertEqual('test_state', private.transition('test_state'))
        self.assertEqual('test_state', manager.instance.state)


class StateMachineTestCase(TestCase):

    def test_class_exists(self):
        StateMachine

    def test_create_statemachine(self):
        sm = TestStateMachine()
        self.assertEqual('private', sm.state.value)

    def test_get_choices(self):
        self.assertIn(('private', 'Private'), TestStateMachine.get_choices())
        self.assertIn(('public', 'Public'), TestStateMachine.get_choices())

    def test_transition(self):
        instance = TestModel(name='Test Model 1', state='private')
        sm = TestStateMachine(instance=instance)
        sm.transition('publish')
        self.assertEqual('public', instance.state)
        self.assertEqual('public', sm.state.value)

    def test_invalid_action(self):
        sm = TestStateMachine(
            instance=TestModel(name='Test Model 1', state='private'))

        with self.assertRaises(InvalidTransition):
            sm.transition('retract')

    def test_with_instance(self):
        instance = TestModel.objects.create(
            name='Test Model 1',
            state='private')
        sm = TestStateMachine(instance=instance)

        sm.transition('publish')
        instance.save()

        self.assertEqual('public', instance.state)
        self.assertEqual('Object made public', instance.message)

    def test_with_instance_custom_state_field(self):
        instance = TestModel.objects.create(
            name='Test Model 1',
            state='private')

        sm = TestStateMachine(instance=instance, state_field='other_state')

        sm.transition('publish')
        instance.save()

        self.assertEqual('private', instance.state)
        self.assertEqual('public', instance.other_state)

    def test_get_available_actions(self):
        temp = TestModel.objects.create(name='Test Model 1', state='private')
        sm = TestStateMachine(instance=temp, state_field='other_state')
        self.assertEqual(
            (('publish', 'Publish'),),
            sm.actions)

    def test_get_permissions(self):
        perms = TestStateMachine.get_permissions('testmodel')
        expected_perms = (
            ('private_view_testmodel', '[Private] Can View Testmodel'),
            ('private_edit_testmodel', '[Private] Can Edit Testmodel'),
            ('private_delete_testmodel', '[Private] Can Delete Testmodel'),

            ('public_view_testmodel', '[Public] Can View Testmodel'),
            ('public_edit_testmodel', '[Public] Can Edit Testmodel'),
            ('public_delete_testmodel', '[Public] Can Delete Testmodel'),

            ('can_publish_testmodel', 'Can Publish Testmodel'),
            ('can_retract_testmodel', 'Can Retract Testmodel'),
        )

        for p in expected_perms:
            self.assertIn(p, perms)


class NumberedStateMachineTestCase(TestCase):

    def test_create_statemachine(self):
        sm = TestIntegerStateMachine()
        self.assertEqual(1, sm.state.value)
        self.assertEqual('Private', sm.state.verbose_name)

    def test_perform_action(self):
        instance = TestModel.objects.create(name='Test Model 1', state_num=1)
        sm = TestIntegerStateMachine(instance=instance)
        sm.transition('publish')

        self.assertEqual(2, sm.state.value)
        self.assertEqual('Public', sm.state.verbose_name)

    def test_get_choices(self):
        self.assertEqual(
            ((1, 'Private'), (2, 'Public')),
            TestIntegerStateMachine.get_choices()
        )

    def test_get_permissions(self):
        expected_perms = (
            ('1_view_testmodel', '[Private] Can View Testmodel'),
            ('1_edit_testmodel', '[Private] Can Edit Testmodel'),
            ('1_delete_testmodel', '[Private] Can Delete Testmodel'),
            ('can_publish_testmodel', 'Can Publish Testmodel'),

            ('2_view_testmodel', '[Public] Can View Testmodel'),
            ('2_edit_testmodel', '[Public] Can Edit Testmodel'),
            ('2_delete_testmodel', '[Public] Can Delete Testmodel'),
            ('can_retract_testmodel', 'Can Retract Testmodel'),
        )

        for p in expected_perms:
            self.assertIn(
                p,
                TestIntegerStateMachine.get_permissions('testmodel'))

    def test_get_available_actions(self):
        temp = TestModel.objects.create(name='Test Model 1', state_num=1)
        sm = TestIntegerStateMachine(instance=temp, state_field='state_num')
        self.assertEqual(
            (('publish', 'Publish'),),
            sm.actions)

    def test_with_instance(self):
        instance = TestModel.objects.create(name='Test Model 1', state_num=1)
        sm = TestIntegerStateMachine(
            instance=instance,
            state_field='state_num')

        sm.transition('publish')
        instance.save()

        self.assertEqual(2, instance.state_num)
        self.assertEqual(2, sm.state.value)
        self.assertEqual('Object made public', instance.message)
