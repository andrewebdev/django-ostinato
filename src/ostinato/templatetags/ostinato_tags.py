import re

from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ostinato.models import ContentItem
from ostinato.forms import ContentItemForm

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
    breadcrumbs = ContentItem.objects.get_breadcrumbs_for(content_item)
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
@register.inclusion_tag('ostinato/tags/toolbar.html', takes_context=True)
def ostinato_toolbar(context, cms_item, allowed_users="is_staff=True"):
    """
    The ostinato toolbar is a bar that renders basic ostinato functions and
    actions that will allow users to create new pages, edit the meta for
    pages etc.

    ``cms_item`` is the ostinato.ContentItem instance for the current content
    item. The easiest way to retrieve this in the template is to use the
    ``get_cmsitem`` template tag.

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
        to_return['cms_item_form'] = ContentItemForm(instance=cms_item)

    # Get the ostinato item
    to_return['cms_item'] = cms_item

    return to_return


## ContentModifiers and related examples
class ContentMod(object):
    """
    Special class to register render functions that will manipulate
    blog content in some way. These functions are accessed by the
    ``embed()`` filter below.
    """
    _modifiers = []

    @classmethod
    def register(cls, func_name, func):
        cls._modifiers.append({'name': func_name, 'func': func})

    def modifiers(self, exclude=[]):
        to_return = []
        for func in self._modifiers:
            if func['name'] not in exclude:
                to_return.append(func['func'])
        return to_return

    def __getitem__(self, what):
        for func in self._modifiers:
            if func['name'] == what: return func['func']
        raise Exception('%s is not a valid Content Modifier' % what)


@register.filter(name='modify')
def modify(content, mods=None):
    """
    This filter will call func() with content being passed to it as a
    string.

    ``mods`` is a comma seperated list of modifiers that we want the
    content to be passed through.

    There are three ways in which this filter can be used.

    1. if ``mods`` is not supplied, then by default we will run the
    content through _all_ modifiers

    2. if ``mods`` is supplied, then we will only run the content through
    modifiers specified in the list.

    3. if ``mods`` starts with "!" we will use all modifiers, _except_
    for any modifiers in the list immediately following the "!"

    Examples:
        {{ content|modify }}
        {{ content|modify:"youtube,gallery" }}
        {{ content|modify:"!snip,youtube" }}

    """
    cm = ContentMod()
    if mods:
        if mods[0] == "!":
            # Exclusion List
            mods = mods[1:].split(',')
            for func in cm.modifiers(exclude=mods):
                content = func(content)
        else:
            # Inclusion List
            mods = mods.split(',')
            for mod in mods:
                content = cm[mod](content)
    else:
        for func in cm.modifiers():
            content = func(content)
    return content


def youtube(content):
    """
    Looks for any youtube url patterns in content, and replaces it with
    the youtube video
    """
    regex = re.compile(r"(http://)?(www\.)?((youtu\.be/)|(youtube\.com/watch\?v=))(?P<id>[A-Za-z0-9\-=_]{11})")
    return regex.sub('''
        <iframe width="480" height="390"
            src="http://www.youtube.com/embed/\g<id>" frameborder="0"
            allowfullscreen></iframe>
    ''', content)


def snip(content):
    """
    This is a special modifier, that will look for a marker in
    ``content`` and if found, it will truncate the content at that
    point.

    This way the editor can decide where he wants content to be truncated,
    for use in the various list views.

    The marker we will look for in the content is {{{snip}}}
    """
    return content[:content.find('{{{snip}}}')] + "..."


def hide_snip(content):
    return content.replace('{{{snip}}}', '')


ContentMod.register('youtube', youtube)
ContentMod.register('snip', snip)
ContentMod.register('hide_snip', hide_snip)