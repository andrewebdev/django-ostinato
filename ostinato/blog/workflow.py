from django.utils import timezone
from ostinato.statemachine import State, StateMachine, action


def publish(instance, **kwargs):
    if instance.publish_date is None:
        instance.publish_date = timezone.now()


def retract(instance, **kwargs):
    if kwargs.get('reset_publish_date', False):
        instance.publish_date = None


class Private(State):
    value = 'private'
    verbose_name = 'Private'

    @action('review', verbose_name='Send for Review')
    def review(self, **kwargs):
        # Usually we send email here to the reviewers
        pass

    @action('published')
    def publish(self, **kwargs):
        if self.manager.instance:
            publish(self.manager.instance, **kwargs)


class Review(State):
    value = 'review'
    verbose_name = 'Review'

    @action('private')
    def reject(self, **kwargs):
        pass

    @action('published')
    def approve(self, **kwargs):
        if self.manager.instance:
            publish(self.manager.instance, **kwargs)


class Published(State):
    value = 'published'
    verbose_name = 'Published'

    @action('archived')
    def archive(self, **kwargs):
        if self.manager.instance:
            self.manager.instance.allow_comments = False
            self.manager.instance.archived_date = timezone.now()

    @action('private')
    def retract(self, **kwargs):
        if self.manager.instance:
            retract(self.manager.instance, **kwargs)


class Archived(State):
    value = 'archived'
    verbose_name = 'Archived'

    @action('private')
    def retract(self, **kwargs):
        if self.manager.instance:
            retract(self.manager.instance, **kwargs)


class BlogEntryWorkflow(StateMachine):
    states = (
        Private,
        Review,
        Published,
        Archived,
    )
    initial_state = Private
