from django import template
from ostinato.pages.models import Page


register = template.Library()


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


@register.simple_tag
def get_page(ignore_sites=False, **kwargs):
    """
    A handy helper that returns the first page filtered by **kwargs
    """
    try:
        return Page.objects.filter(**kwargs)[0]
    except IndexError:
        return None


@register.simple_tag
def filter_pages(ignore_sites=False, **kwargs):
    """
    A handy helper that can search for a list of pages filtered by **kwargs.
    """
    return Page.objects.filter(**kwargs)
