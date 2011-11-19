from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


class GetStateMachineNode(template.Node):

    def __init__(self, statemachine, object_instance):
        self.statemachine = statemachine
        self.object_instance = object_instance

    def render(self, context):
        app_label, model = self.statemachine.split('.')
        statemachine_type = ContentType.objects.get_by_natural_key(
            app_label, model)

        statemachine = statemachine_type.model_class().objects.get_statemachine(
            self.object_instance)
        context['statemachine'] = statemachine
        return ''
