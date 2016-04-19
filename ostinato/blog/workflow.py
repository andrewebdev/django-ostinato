from django.utils import timezone
from ostinato.statemachine import State, IntegerStateMachine


def publish(instance, **kwargs):
    if instance.publish_date is None:
        instance.publish_date = timezone.now()

def retract(instance, **kwargs):
    if kwargs.get('reset_publish_date', False):
        instance.publish_date = None


class Private(State):
    verbose_name = 'Private'
    transitions = {'review': 3, 'publish': 5}

    def publish(self, **kwargs):
        publish(self.instance, **kwargs)


class Review(State):
    verbose_name = 'Review'
    transitions = {'reject': 1, 'approve': 5}

    def approve(self, **kwargs):
        publish(self.instance, **kwargs)


class Published(State):
    verbose_name = 'Published'
    transitions = {'retract': 1, 'archive': 10}

    def archive(self, **kwargs):
        self.instance.allow_comments = False
        self.instance.archived_date = timezone.now()

    def retract(self, **kwargs):
        retract(self.instance, **kwargs)


class Archived(State):
    verbose_name = 'Archived'
    transitions = {'retract': 1}

    def retract(self, **kwargs):
        retract(self.instance, **kwargs)


class BlogEntryWorkflow(IntegerStateMachine):
    state_map = {1: Private, 3: Review, 5: Published, 10: Archived}
    initial_state = 1

