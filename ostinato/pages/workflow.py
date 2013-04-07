from django.conf import settings
from django.utils import timezone

from ostinato.statemachine import State, IntegerStateMachine


DEFAULT_STATE = getattr(settings, 'OSTINATO_PAGES_DEFAULT_STATE', 5)


class Private(State):
    verbose_name = 'Private'
    transitions = {'publish': 5}

    def publish(self, **kwargs):
        if self.instance and not self.instance.publish_date:
            self.instance.publish_date = timezone.now()


class Published(State):
    verbose_name = 'Published'
    transitions = {'retract': 1, 'archive': 10}


class Archived(State):
    verbose_name = 'Archived'
    transitions = {'retract': 1}


class PageWorkflow(IntegerStateMachine):
    state_map = {1: Private, 5: Published, 10: Archived}
    initial_state = DEFAULT_STATE


def get_workflow():
    """
    This is a helper function that returns the correct workflow to be used.
    This is required since we provide a setting that allows the developer
    to change the statemachine that should manage Pages.
    """
    custom_workflow = getattr(settings, 'OSTINATO_PAGES_WORKFLOW_CLASS', None)
    if custom_workflow:
        import_path, statemachine = custom_workflow.rsplit('.', 1)
        cl = __import__(import_path, locals(), globals(), [statemachine], -1)\
            .__dict__[statemachine]
        return cl
    else:
        return PageWorkflow