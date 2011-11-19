from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class StateMachineBase(models.Model):

    state = models.CharField(max_length='50', editable=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('content_type', 'object_id'),)
        abstract = True

    def __unicode__(self):
        return '%s, %d (%s)' % (self.content_type.name, self.object_id, self.state)

    def get_actions(self):
        return self.SMOptions.state_actions[self.state]

    def take_action(self, action):
        if action in self.get_actions():
            self.state = self.SMOptions.action_targets[action]


class DefaultStateMachine(StateMachineBase):

    class Meta:
        """
        These are basic admin permissions and will be used as intended.
        They do however serve a second purpose, which is basically a list of
        'actions' that can be taken on the statemachine, by the user.
        """
        permissions = (
            ('can_submit', 'Can submit for review'),
            ('can_reject', 'Can reject'),
            ('can_publish', 'Can publish'),
            ('can_retract', 'Can retract'),
            ('can_archive', 'Can archive'),
        )

    class SMOptions:
        state_actions = {
            'private': ('can_submit', 'can_publish'),
            'review': ('can_publish', 'can_reject'),
            'published': ('can_retract', 'can_archive'),
            'archived': ('can_retract',)
        }
        action_targets = {
            'can_submit': 'review',
            'can_reject': 'private',
            'can_publish': 'published',
            'can_retract': 'private',
            'can_archive': 'archived'
        }
