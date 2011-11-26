from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import Signal

from managers import StateMachineManager

class InvalidAction(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


sm_pre_action = Signal(providing_args=['action', 'user'])
sm_post_action = Signal(providing_args=['action', 'user'])


class StateMachineBase(models.Model):

    state = models.CharField(max_length='50', editable=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = StateMachineManager()

    class Meta:
        unique_together = (('content_type', 'object_id'),)
        abstract = True

    def __unicode__(self):
        return '%s, %d (%s)' % (self.content_type.name, self.object_id, self.state)

    def save(self, *args, **kwargs):
        if not self.state:
            self.state = self.SMOptions.initial_state
        return super(StateMachineBase, self).save(*args, **kwargs)

    def get_actions(self):
        return self.SMOptions.state_actions[self.state]

    def take_action(self, action):
        if action in self.get_actions():
            sm_pre_action.send(sender=self, instance=self, action=action)
            self.state = self.SMOptions.action_targets[action]
            self.save()
            sm_post_action.send(sender=self, instance=self, action=action)
        else:
            raise InvalidAction('%s is not a valid action. Actions are (%s)' % (
                action, ', '.join(self.get_actions())))


class DefaultStateMachine(StateMachineBase):

    class Meta:
        """
        These are basic admin permissions and will be used as intended.
        They do however serve a second purpose, which is basically a list of
        'actions' that can be taken on the statemachine, by the user.
        """
        permissions = (
            ('submit', 'Can submit for review'),
            ('reject', 'Can reject'),
            ('publish', 'Can publish'),
            ('retract', 'Can retract'),
            ('archive', 'Can archive'),
        )

    class SMOptions:
        initial_state = 'private'
        state_actions = {
            'private': ('submit', 'publish'),
            'review': ('publish', 'reject'),
            'published': ('retract', 'archive'),
            'archived': ('retract',)
        }
        action_targets = {
            'submit': 'review',
            'reject': 'private',
            'publish': 'published',
            'retract': 'private',
            'archive': 'archived'
        }
