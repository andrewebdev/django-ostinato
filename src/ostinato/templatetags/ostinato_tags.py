from django import template

from ostinato.models import ContentItem

register = template.Library()

@register.inclusion_tag('ostinato/tags/navbar.html')
def render_navbar(parent=None):
    """
    Renders the standard navigation bar.

    """
    if parent:
        navbar = ContentItem.objects.get_navbar(parent=parent)
    else:
        navbar = ContentItem.objects.get_navbar()
    return locals()
