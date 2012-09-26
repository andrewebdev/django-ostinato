from django import template

from ostinato.pages.models import Page


register = template.Library()


@register.inclusion_tag('pages/navbar.html', takes_context=True)
def navbar(context, for_page=None, path=''):
    """
    Renders a basic navigation bar.

    ``for_page`` is used to specify a navbar for a specific
        page (it's children); defaults to root level pages

    ``path`` can be used in special cases where a page might not exist on
    the current path, but you would like the page to be "discovered" from the
    url. This will basically mark the active page in the navbar; if it can
    be found in the path of course.

    """
    if 'page' not in context:
        page = Page.objects.get_from_path(path)
    else:
        page = context['page']

    navbar = Page.objects.get_navbar(for_page=for_page)

    return {
        'page': page,
        'navbar': navbar,
    }


@register.inclusion_tag('pages/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, for_page=None):
    """ Renders the breadcrumbs for the current page in the context """
    if not for_page:
        # Attempt to get the page from the context
        try:
            for_page = context['page']
        except KeyError:
            return {}

    breadcrumbs = Page.objects.get_breadcrumbs(for_page=for_page)
    return locals()


@register.assignment_tag  # Requires Django 1.4+
def get_page(slug):
    """ Finds the page with ``slug`` and adds that to the context """
    return Page.objects.get(slug=slug)


