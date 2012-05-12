from django.template import RequestContext

from ostinato.pages.models import Page


def get_page_from_path(request):
    """
    A context processors that will check if a page object exists in the
    context. If not, we will traverse the path, to try and see if any of
    the slugs in the path is for a page. If so, we add that page to the
    context.
    """
    c = RequestContext(request)
    if 'page' not in c:
        return {'page': Page.objects.get_from_path(request.path)}

