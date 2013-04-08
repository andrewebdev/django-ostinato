from django.utils import timezone

from ostinato.statemachine import State, IntegerStateMachine


class Private(State):
    verbose_name = 'Private'
    transitions = {'review': 3, 'publish': 5}

    def publish(self, **kwargs):
        if self.instance and self.instance.publish_date is None:
            self.instance.publish_date = timezone.now()


class Review(State):
    verbose_name = 'Review'
    transitions = {'reject': 1, 'approve': 5}

    def approve(self, **kwargs):
        if self.instance and self.instance.publish_date is None:
            self.instance.publish_date = timezone.now()


class Published(State):
    verbose_name = 'Published'
    transitions = {'retract': 1, 'archive': 10}

    def archive(self, **kwargs):
        if self.instance:
            self.instance.allow_comments = False
            self.archive_date = timezone.now()

    def retract(self, **kwargs):
        if self.instance and kwargs.get('reset_publish_date', False):
            self.instance.publish_date = None


class Archived(State):
    verbose_name = 'Archived'
    transitions = {'retract': 1}

    def retract(self, **kwargs):
        if self.instance and kwargs.get('reset_publish_date', False):
            self.instance.publish_date = None


class BlogEntryWorkflow(IntegerStateMachine):
    state_map = {1: Private, 3: Review, 5: Published, 10: Archived}
    initial_state = 1