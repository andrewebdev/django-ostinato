import re

from django import template

register = template.Library()


## ContentModifiers and related examples
class ContentMod(object):
    """
    Special class to register render functions that will manipulate
    text content in some way. These functions are accessed by the
    ``modify`` filter below.
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