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
    navbar = Page.objects.get_navbar(for_page=for_page)
    return locals()


@register.inclusion_tag('pages/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, for_page=None):
    """ Renders the breadcrumbs for the current page in the context """
    if not for_page:
        # Attempt to get the page from the context
        for_page = context['page']

    breadcrumbs = Page.objects.get_breadcrumbs(for_page=for_page)
    return locals()


@register.assignment_tag  # Requires Django 1.4+
def get_page(slug):
    """ Finds the page with ``slug`` and adds that to the context """
    return Page.objects.get(slug=slug)

