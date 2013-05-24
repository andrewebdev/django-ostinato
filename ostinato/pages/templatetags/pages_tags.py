from django import template
from django.conf import settings

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
    navbar = Page.objects.get_navbar(for_page=for_page)
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
def get_page(ignore_sites=False, **kwargs):
    """
    A handy helper that returns the first page filtered by **kwargs
    """
    PAGES_SITE_TREEID = getattr(settings, 'OSTINATO_PAGES_SITE_TREEID', None)

    if PAGES_SITE_TREEID and not ignore_sites:
        kwargs.update({'tree_id': PAGES_SITE_TREEID})
    try:
        return Page.objects.filter(**kwargs)[0]
    except IndexError:
        return None


@register.assignment_tag
def filter_pages(ignore_sites=False, **kwargs):
    """
    A handy helper that can search for a list of pages filtered by **kwargs.
    """
    PAGES_SITE_TREEID = getattr(settings, 'OSTINATO_PAGES_SITE_TREEID', None)

    if PAGES_SITE_TREEID and not ignore_sites:
        kwargs.update({'tree_id': PAGES_SITE_TREEID})
    return Page.objects.filter(**kwargs)
