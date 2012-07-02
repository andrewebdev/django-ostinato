from django.views.generic import View, TemplateView
from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
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
        path = kwargs['path'].split('/')

        if not path[-1]:
            path = path[:-1]

        page = get_object_or_404(Page, slug=path[-1])

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

