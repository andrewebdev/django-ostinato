from django.dispatch import Signal
from django.conf import settings


class InvalidStateMachine(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class InvalidAction(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

pre_action = Signal(providing_args=['action', 'user'])
post_action = Signal(providing_args=['action', 'user'])

class StateMachine(object):
    """
    Any model that wishes to use this statemachine can simply
    inherrit from it.

    Note that this model assumes you have a ``sm_state`` field
    defined in your main model.
    """
    SM_ACTIONS = [
        {'action': 'submit',
         'help_text': 'Submit document for review',
         'target': 'review'
        },
        {'action': 'publish',
         'help_text': 'Publish this document',
         'target': 'published'
        },
        {'action': 'reject',
         'help_text': 'Reject the document based',
         'target': 'private'
        },
        {'action': 'archive',
         'help_text': 'Archive this document',
         'target': 'archived'
        },
    ]
    SM_STATEMACHINE = [
        {'state': 'private', 'actions': ['submit', 'publish']},
        {'state': 'review', 'actions': ['publish', 'reject']},
        {'state': 'published', 'actions': ['retract', 'archive']},
        {'state': 'archived', 'actions': ['retract']},
    ]

    def init_statemachine(self):
        if not self.sm_state: # Set default state
            self.sm_state = self.SM_STATEMACHINE[0]['state']

    def sm_state_actions(self):
        """
        Returns a list of actions available for the current state.
        """
        return self._get_state(self.sm_state)['actions']

    def _get_action(self, action):
        for item in self.SM_ACTIONS:
            if action == item['action']: return item

    def _get_state(self, state):
        """ Get a specific state dict from the statemachine """
        for item in self.SM_STATEMACHINE:
            if state == item['state']: return item

    def sm_take_action(self, action, user=None):
        """
        Take an action to change the state and send the apropriate signals.
        """
        if action in self.sm_state_actions():
            pre_action.send(sender=self, instance=self,
                            action=action, user=user)
            self.sm_state = self._get_action(action)['target']
            self.save()
            post_action.send(sender=self, instance=self,
                             action=action, user=user)
        else:
            raise InvalidAction('Invalid action, %s. Choices are, %s' % (
                action, ','.join(self.sm_state_actions())))
