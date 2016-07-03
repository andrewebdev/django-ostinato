from django import http
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from .core import get_browsers, BrowserNotFound


def browser_dispatch(request, browser_id):
    try:
        browser = get_browsers(browser_id)
    except BrowserNotFound:
        raise http.Http404
    return browser.as_view()(request)


class BrowserView(TemplateView):
    title = "Untitled"
    description = ""
    browser_id = None
    template_name = None

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BrowserView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = super(BrowserView, self).get_context_data(**kwargs)
        c['browser'] = self.browser_id
        c['item_list'] = self.get_items(self.request)
        c['field_name'] = self.request.GET.get('field_name', None)
        return c

    def get_items(self, request):
        name = self.__class__.__name__
        raise NotImplementedError(
            'get_items() method not found for, %s ContentBrowser' % name)
