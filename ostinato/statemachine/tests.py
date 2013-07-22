import json

from django.test import TestCase
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission

from ostinato.statemachine import State, StateMachine
from ostinato.statemachine import (
    InvalidState, InvalidTransition, InvalidStateMachine)
from ostinato.statemachine.views import StateActionView


# Create some states and a StateMachine
class Private(State):
    verbose_name = 'Private'
    transitions = {'publish': 'public'}

    def publish(self, msg="Object made public"):
        if self.instance:
            self.instance.message = msg


class Public(State):
    verbose_name = 'Public'
    transitions = {'retract': 'private'}

    def retract(self):
        if self.instance:
            self.instance.message = 'Object made private'


class ErrorState(State):
    verbose_name = 'Error State'
    transitions = {'invalid_action': 'invalid'}  # Target state does not exist


class HangingState(State):
    verbose_name = 'Hanging State'
    transitions = {}


class TestStateMachine(StateMachine):
    state_map = {'private': Private, 'public': Public}
    initial_state = 'private'


class InvalidSM(StateMachine):
    state_map = {'private': Private, 'error': ErrorState, 'public': Public}
    initial_state = 'invalid'


class ErrorSM(InvalidSM):
    initial_state = 'private'


class HangingSM(InvalidSM):
    state_map = {'private': Private, 'hanging': HangingState, 'public': Public}
    initial_state = 'private'


# Create a test model to test the StateMachine with
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=20, null=True, blank=True)
    state_num = models.IntegerField(null=True, blank=True)
    other_state = models.CharField(max_length=20, null=True, blank=True)
    message = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        permissions = TestStateMachine.get_permissions('testmodel', 'Test')


# Now test the states and statemachine
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


class StateMachineViewsTestCase(TestCase):
    """
    Statemachine views that allows for taking actions on a specific model
    """
    urls = 'ostinato.statemachine.test_urls'

    def setUp(self):
        # Create a test user with the correct permission
        self.user = User.objects.create(username='test', password='secret', email='test@example.com')
        self.user.set_password('secret')
        self.user.save()

        TestModel.objects.create(name='Test Model 1', state='private')
        self.data = json.dumps({
            "statemachine": "ostinato.statemachine.tests.TestStateMachine",
            "action": "publish",
            "next": "/",
            "action_kwargs": {"msg": "Custom kwargs for actions"},
        })

    def test_view_exists(self):
        StateActionView

    def test_url_reverse_lookup(self):
        self.assertEqual(
            '/app/model/1/',
            reverse('statemachine_action', kwargs={
                'app_label': 'app',
                'model': 'model',
                'obj_id': 1
            }))

    def test_get_raises_405(self):
        response = self.client.get('/app/model/1/')
        self.assertEqual(405, response.status_code)

    def test_correct_permission_required(self):
        response = self.client.put(
            '/statemachine/testmodel/1/',
            data=self.data, content_type='application/json')

        self.assertEqual(403, response.status_code)

    def test_put_success_response(self):
        perm = Permission.objects.get(codename='can_publish_testmodel')
        self.user.user_permissions.add(perm)
        self.user.save()

        self.client.login(username='test', password='secret')
        response = self.client.put(
            '/statemachine/testmodel/1/',
            data=self.data, content_type="application/json", follow=True)

        self.assertEqual([(u'http://testserver/', 302)],
                         response.redirect_chain)

    def test_put_takes_action_on_statemachine(self):
        perm = Permission.objects.get(codename='can_publish_testmodel')
        self.user.user_permissions.add(perm)
        self.user.save()

        self.client.login(username='test', password='secret')
        self.client.put(
            '/statemachine/testmodel/1/',
            data=self.data, content_type="application/json")

        obj = TestModel.objects.get(id=1)
        self.assertEqual(u'public', obj.state)

        # Check that the action kwargs was also passed
        self.assertEqual('Custom kwargs for actions', obj.message)

    def test_put_response_without_correct_permission(self):
        perm = Permission.objects.get(codename='can_publish_testmodel')
        self.user.user_permissions.add(perm)
        self.user.save()

        TestModel.objects.all().update(state='public')

        self.client.login(username='test', password='secret')
        response = self.client.put(
            '/statemachine/testmodel/1/',
            data=self.data, content_type="application/json")

        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "publish is not a valid action. Valid actions are: ['retract']",
            response.content)

    def test_put_ajax_response(self):
        perm = Permission.objects.get(codename='can_publish_testmodel')
        self.user.user_permissions.add(perm)
        self.user.save()

        self.client.login(username='test', password='secret')
        response = self.client.put(
            '/statemachine/testmodel/1/',
            data=self.data, content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        expected_data = {
            u"status": u"ok",
            u"state_before": u"Private",
            u"state_after": u"Public",
            u"action_taken": u"publish",
        }
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_data, json.loads(response.content))
