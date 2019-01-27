from importlib import import_module
from ostinato.statemachine import State, StateMachine
from ostinato.pages import PAGES_SETTINGS


DEFAULT_STATE = PAGES_SETTINGS.get('default_state')


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
    The workflow used for pages can be overridden using the `workflow_class`
    setting in `OSTINATO_PAGES` setting.
    """
    workflow_class = PAGES_SETTINGS.get('workflow_class')
    import_path, statemachine = workflow_class.rsplit('.', 1)
    return getattr(import_module(import_path), statemachine)
