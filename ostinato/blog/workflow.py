from django.utils import timezone
from ostinato.statemachine import State, StateMachine


def publish(instance, **kwargs):
    if instance.publish_date is None:
        instance.publish_date = timezone.now()

def retract(instance, **kwargs):
    if kwargs.get('reset_publish_date', False):
        instance.publish_date = None


class Private(State):
    verbose_name = 'Private'
    transitions = {'review': 'review', 'publish': 'published'}

    def publish(self, **kwargs):
        publish(self.instance, **kwargs)


class Review(State):
    verbose_name = 'Review'
    transitions = {'reject': 'private', 'approve': 'published'}

    def approve(self, **kwargs):
        publish(self.instance, **kwargs)


class Published(State):
    verbose_name = 'Published'
    transitions = {'retract': 'private', 'archive': 'archived'}

    def archive(self, **kwargs):
        self.instance.allow_comments = False
        self.instance.archived_date = timezone.now()

    def retract(self, **kwargs):
        retract(self.instance, **kwargs)


class Archived(State):
    verbose_name = 'Archived'
    transitions = {'retract': 'private'}

    def retract(self, **kwargs):
        retract(self.instance, **kwargs)


class BlogEntryWorkflow(StateMachine):
    state_map = {
        'private': Private,
        'review': Review,
        'published': Published,
        'archived': Archived
    }
    initial_state = 'private'

