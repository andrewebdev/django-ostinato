from django.views.generic import View, TemplateView
from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse, resolve, Resolver404
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django import http

from ostinato.pages.models import Page, PageWorkflow
from ostinato.pages.forms import MovePageForm


def page_dispatch(request, *args, **kwargs):
    """
    This is our main entry-point for pages. From here we will determine
    what page we are working with, check if that page has a custom view.

    If the page has a custom view, we will dispatch to that view, otherwise
    we will use our default ``PageView``
    """

    ## Some basic page checking and authorization
    if 'path' in kwargs:
        page, sub_path = Page.objects.get_from_path(kwargs['path'])

        if not page:
            raise http.Http404

        # Here we check for sub_path and if the current page allows for that
        if page and sub_path:
            content = page.get_content_model()

            if content.ContentOptions.urls:
                if settings.APPEND_SLASH:
                    sub_path += '/'
                try:
                    pattern = resolve(sub_path, content.ContentOptions.urls)
                except Resolver404:
                    raise http.Http404

                if pattern:
                    view, args, kwargs = pattern
                    # Now return the view, but make sure to add our page
                    # to the context first
                    kwargs.update({'page': page})
                    return view(request, *args, **kwargs)

            raise http.Http404

    else:
        # If we are looking at the root object, show the first root page
        try:
            page = Page.tree.root_nodes()[0]
        except IndexError:
            raise http.Http404

    sm = PageWorkflow(instance=page)
    if sm.state == 'Private' and not request.user.has_perm('pages.private_view'):
        if page.author != request.user or not request.user.is_superuser:
            return http.HttpResponseForbidden()

    content = page.get_content_model()

    ## Check if the page has a custom view
    if hasattr(content.ContentOptions, 'view'):
        module_path, view_class = content.ContentOptions.view.rsplit('.', 1)

        # Import our custom view
        v = __import__(module_path, locals(), globals(), [view_class], -1)\
            .__dict__[view_class]

        return v.as_view(page=page)(request, *args, **kwargs)

    else:
        return PageView.as_view(page=page)(request, *args, **kwargs)


class PageView(TemplateView):

    page = None

    def get_context_data(self, **kwargs):
        c = super(PageView, self).get_context_data(**kwargs)
        self.template_name = self.page.get_template()
        c['page'] = self.page
        return c


class PageReorderView(View):

    @method_decorator(staff_member_required)
    def post(self, *args, **kwargs):
        form = MovePageForm(self.request.POST)

        if form.is_valid():
            form.save()

        return http.HttpResponseRedirect(reverse('admin:pages_page_changelist'))


## A Custom View Example
class CustomView(PageView):

    def get_context_data(self, **kwargs):
        c = super(CustomView, self).get_context_data(**kwargs)
        c['custom'] = 'Some Custom Context'
        return c

