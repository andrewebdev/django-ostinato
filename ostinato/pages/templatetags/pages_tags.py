from django import template

from ostinato.pages.models import Page


register = template.Library()


@register.inclusion_tag('pages/navbar.html', takes_context=True)
def navbar(context, for_page=None):
    """
    Renders a basic navigation bar.

    ``for_page`` is used to specify a navbar for a specific
        page (it's children); defaults to root level pages
    """
    page = context.get('page', None)

    if for_page and not for_page.is_leaf_node():
        navbar = Page.objects.get_navbar(for_page=for_page)
    else:
        # Return root level pages
        navbar = Page.objects.get_navbar(for_page=None)

    return {
        'page': page,
        'navbar': navbar,
    }


@register.inclusion_tag('pages/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, for_page=None, obj=None):
    """ Renders the breadcrumbs for the current page in the context """
    if not for_page:
        # Attempt to get the page from the context
        try:
            for_page = context['page']
        except KeyError:
            return {}

    breadcrumbs = Page.objects.get_breadcrumbs(for_page=for_page)

    if obj:
        # Note that title and get_absolute_url() is required for the custom
        # object.
        breadcrumbs.append({
            'title': obj.title,
            'url': obj.get_absolute_url(),
        })

    return {
        "breadcrumbs": breadcrumbs,
        "for_page": for_page
    }


@register.assignment_tag  # Requires Django 1.4+
def get_page(**kwargs):
    """
    A handy helper that returns the first page filtered by **kwargs
    """
    try:
        return Page.objects.filter(**kwargs)[0]
    except:
        return None


@register.assignment_tag
def filter_pages(**kwargs):
    """
    A handy helper that can search for a list of pages filtered by **kwargs.
    """
    try:
        return Page.objects.filter(**kwargs)
    except:
        return None