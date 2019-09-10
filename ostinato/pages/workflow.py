from importlib import import_module
from django.utils import timezone
from ostinato.statemachine import State, StateMachine, action
from ostinato.pages import PAGES_SETTINGS


def get_default_state():
    """
    This is a helper function that returns the correct workflow to be used.
    The workflow used for pages can be overridden using the `workflow_class`
    setting in `OSTINATO_PAGES` setting.
    """
    state_class = PAGES_SETTINGS.get('default_state')
    import_path, state = state_class.rsplit('.', 1)
    return getattr(import_module(import_path), state)


def get_workflow():
    """
    This is a helper function that returns the correct workflow to be used.
    The workflow used for pages can be overridden using the `workflow_class`
    setting in `OSTINATO_PAGES` setting.
    """
    workflow_class = PAGES_SETTINGS.get('workflow_class')
    import_path, statemachine = workflow_class.rsplit('.', 1)
    return getattr(import_module(import_path), statemachine)


class Private(State):
    value = 'private'
    verbose_name = 'Private'

    @action('public', verbose_name='Make public')
    def publish(self, **kwargs):
        if self.manager.instance:
            if not self.manager.instance.publish_date:
                self.manager.instance.publish_date = timezone.now()


class Public(State):
    value = 'public'
    verbose_name = 'Public'

    @action('private', verbose_name='Make private')
    def retract(self, **kwargs):
        pass


class PageWorkflow(StateMachine):
    states = (Private, Public)
    initial_state = get_default_state()
