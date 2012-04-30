from django import template

from ostinato.pages.models import Page


register = template.Library()


@register.inclusion_tag('pages/navbar.html', takes_context=True)
def navbar(context, for_page=None):
    """
    Renders the standard navigation bar.
    ``parent`` specifies the start level for the navbar,
        defaults to root level pages
    """
    if for_page:
        navbar = Page.objects.get_navbar(for_page=for_page)
    else:
        navbar = Page.objects.get_navbar()
        
    return locals()


@register.assignment_tag  # Requires Django 1.4+
def get_page(slug):
    """ Finds the page with ``slug`` and adds that to the context """
    return Page.objects.get(slug=slug)

