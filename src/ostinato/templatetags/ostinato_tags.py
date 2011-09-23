import re

from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ostinato.models import ContentItem

register = template.Library()


@register.inclusion_tag('ostinato/tags/navbar.html')
def navbar(parent=None):
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


@register.inclusion_tag('ostinato/tags/breadcrumbs.html')
def breadcrumbs(content_item):
    """
    Renders the breadcrumbs for content item.

    TODO: Dynamically discover content item
    Try to get the content_item by cycling through the urlpatterns.
    If the urlpattern is found, get that item and return it's content_item
    instance.
    """
    breadcrumbs = ContentItem.objects.get_breadcrumbs(content_item)
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
        if created:
            title = getattr(for_object, 'title', repr(for_object))
            content_item.title = title
            content_item.save()
        context[self.as_varname] = content_item
        return ''


# The following template tags renders the various tools to assist the
# content editor/admin to edit page content, update pages etc.
#
@register.inclusion_tag('ostinato/tags/toolbar.html', takes_context=True)
def ostinato_toolbar(context, allowed_users="is_staff=True"):
    """
    The ostinato toolbar is a bar that renders basic ostinato functions and
    actions that will allow users to create new pages, edit the meta for
    pages etc.

    We can filter what users will have permission to see the toolbar, by
    passing a django querystring to ``allowed_users``. By default, it will only
    allow admins.
    """
    to_return = {}
    user = context['user']

    # Check if the user matches the allowed_users arg
    filter_kwargs = {}
    filter_list = allowed_users.replace(' ', '').split(',')
    for f in filter_list:
        arg = f.split('=')
        filter_kwargs[arg[0]] = arg[1]
    if context['user'] in User.objects.filter(**filter_kwargs):
        to_return['user_can_edit'] = True

    return to_return

"""
    New Tag: {% ostinato_zone 'zone_name' %}

    This tag will render the content for a specific zone.

    We should be able to specify what content types should be available for that zone.
    This can be done in the settings.py file?

    ostinato_zones = [{
        'name': 'h_banner',
        'verbose_name': 'Horizontal Banner',
        'content_items': [
            'flatpages.flatpage',
            'tehblog.entry',
        ],
        'renderer': ''
    }]

    * How will we define a renderer?
    * How will a renderer work?
        
"""