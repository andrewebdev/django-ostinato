from importlib import import_module
from django.conf import settings
from ostinato.statemachine import State, StateMachine


DEFAULT_STATE = getattr(settings, 'OSTINATO_PAGES_DEFAULT_STATE', 'public')


class Private(State):
    verbose_name = 'Private'
    transitions = {'make_public': 'public'}


class Public(State):
    verbose_name = 'Public'
    transitions = {'make_private': 'private'}


class PageWorkflow(StateMachine):
    state_map = {'private': Private, 'public': Public}
    initial_state = DEFAULT_STATE


def get_workflow():
    """
    This is a helper function that returns the correct workflow to be used.
    A developer can change the default workflow behaviour using the
    ``OSTINATO_PAGES_WORKFLOW_CLASS`` setting.
    """
    custom_workflow = getattr(settings, 'OSTINATO_PAGES_WORKFLOW_CLASS', None)
    if custom_workflow:
        import_path, statemachine = custom_workflow.rsplit('.', 1)
        return getattr(import_module(import_path), statemachine)
    else:
        return PageWorkflow
