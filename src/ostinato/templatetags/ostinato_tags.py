import re

from django import template
from django.contrib.contenttypes.models import ContentType

from ostinato.models import ContentItem

register = template.Library()

@register.inclusion_tag('ostinato/tags/navbar.html')
def render_navbar(parent=None):
    """
    Renders the standard navigation bar.
    ``parent`` specifies the start level for the navbar
    ``depth`` specifies how deep we should show navbar elements. 
    """
    if parent:
        navbar = ContentItem.objects.get_navbar(parent=parent)
    else:
        navbar = ContentItem.objects.get_navbar()
    return locals()

@register.simple_tag
def active_link(request, pattern):
    if request:
        if re.search(pattern, request.path):
            return 'active'
    return ''

@register.tag()
def get_cmsitem(parser, token):
    tokens = token.contents.split()
    if len(tokens) != 5:
        raise template.TemplateSyntaxError("Incorrect number of arguments for %r tag" % tokens[0])
    if tokens[1] != 'for':
        raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])
    if tokens[3] != 'as':
        raise template.TemplateSyntaxError("Forth argument in %r tag must be 'as'" % tokens[0])
    return GetContentItemNode(for_object=tokens[2], as_varname=tokens[4])

class GetContentItemNode(template.Node):
    def __init__(self, for_object, as_varname):
        self.for_object = template.Variable(for_object)
        self.as_varname = as_varname

    def render(self, context):
        for_object = self.for_object.resolve(context)
        for_object_type = ContentType.objects.get_for_model(for_object)
        content_item, created = ContentItem.objects.get_or_create(
            content_type=for_object_type, object_id=for_object.id)
        context[self.as_varname] = content_item
        return ''
