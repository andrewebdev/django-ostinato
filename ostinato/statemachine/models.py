from django.db import models, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import Signal

from ostinato.statemachine.managers import StateMachineManager


class InvalidAction(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


sm_pre_action = Signal(providing_args=['action'])
sm_post_action = Signal(providing_args=['action', 'old_state'])


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


    def get_action_display(self, action):
        for i in self._meta.permissions:
            if i[0] == action:
                return i[1]


    def take_action(self, action):
        if action in self.get_actions():

            sm_pre_action.send(sender=self, action=action)

            old_state = self.state
            self.state = self.SMOptions.action_targets[action]
            self.save()

            sm_post_action.send(sender=self, action=action, old_state=old_state)

        else:
            raise InvalidAction('%s is not a valid action. Actions are (%s)' % (
                action, ', '.join(self.get_actions())))


class StateMachineField(object):
    """
    A custom field that can be added to a model to create a statemachine.
    """
    def __init__(self, statemachine_cls):
        self.statemachine_cls = statemachine_cls

    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)

        self.name = name
        self.model = cls
        self.cache_attr = '_%s_cache' % name

        cls._meta.add_virtual_field(self)

    def __get__(self, instance, instance_type=None):
        ## FIXME:
        # Statemachine get_statemachine() cannot create a object since
        # the related item doesnt have an ID yet (not been created)
        if instance.pk:
            return self.statemachine_cls.objects.get_statemachine(instance)


## This is how we create an actual StateMachine
class DefaultStateMachine(StateMachineBase):

    class Meta:
        """
        These are basic admin permissions and will be used as intended.
        They do however serve a second purpose, which is basically a list of
        'actions' that can be taken on the statemachine, by the user.
        """
        permissions = (
            ('submit', 'Submit for review'),
            ('reject', 'Reject'),
            ('publish', 'Publish'),
            ('retract', 'Retract'),
            ('archive', 'Archive'),
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

