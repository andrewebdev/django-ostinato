from django.db import models
from django.contrib.contenttypes.models import ContentType


class StateMachineManager(models.Manager):

    def get_statemachine(self, object_instance):
        """
        A method that will try to get the statemachine for ``object_instance``.
        If the statemachine for that item does not exist, create it.

        Returns the StateMachine instance
        """
        ctype = ContentType.objects.get_for_model(object_instance)
        statemachine, created = self.get_query_set().get_or_create(
            content_type=ctype, object_id=object_instance.id)
        statemachine.save()
        return statemachine
        
    def has_state(self, state, **kwargs):
        """
        First filter all statemachine instances with ``state``.
        extra filter args can also be passed along with kwargs
        """
        return self.get_query_set().filter(state=state, **kwargs)
