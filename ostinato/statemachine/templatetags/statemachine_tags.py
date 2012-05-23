from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.tag(name='get_statemachine')
def do_get_statemachine(parser, token):

    tokens = token.split_contents()
    if len(tokens) > 6:
        raise template.TemplateSyntaxError(
            "Incorrect number of arguments for %r tag" % tokens[0])
    if tokens[2] != 'for':
        raise template.TemplateSyntaxError(
            "Invalid 'for' argument in %r tag" % tokens[0])
    if len(tokens) > 4 and tokens[4] != 'as':
        raise template.TemplateSyntaxError(
            "Invalid 'as' argument in %r tag" % tokens[0])
    statemachine = tokens[1]
    for_object = tokens[3]
    if len(tokens) > 4:
        as_var = tokens[5]
    else:
        as_var = 'statemachine'
    return GetStateMachineNode(statemachine, for_object, as_var)


class GetStateMachineNode(template.Node):
    """
    Gets the statemachine for a object and adds it to the context.

    Usage:
        {% get_statemachine app.statemachinemodel for instance [as templatevar] %}

    By default the statemachine is added to the context as ``statemachine``.
    As seen in the example above, you can change the name for the statemachine
    template var by adding 'as varname'
    """

    def __init__(self, statemachine, for_object, as_var='statemachine'):
        self.statemachine = statemachine
        self.for_object = template.Variable(for_object)
        self.as_var = as_var

    def render(self, context):
        for_object = self.for_object.resolve(context)

        app_label, model = self.statemachine.split('.')
        sm_type = ContentType.objects.get_by_natural_key(app_label, model)
        sm = sm_type.model_class().objects.get_statemachine(for_object)

        context[self.as_var] = sm
        return ''
