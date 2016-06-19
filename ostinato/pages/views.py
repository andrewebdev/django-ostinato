from django.views.generic import View, TemplateView
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django import http

from ostinato.pages.models import Page
from ostinato.pages.workflow import get_workflow
from ostinato.pages.forms import MovePageForm, DuplicatePageForm


def page_dispatch(request, *args, **kwargs):
    """
    This is our main entry-point for pages. From here we will determine
    what page we are working with, check if that page has a custom view.

    If the page has a custom view, we will dispatch to that view, otherwise
    we will use our default ``PageView``
    """
    PAGES_SITE_TREEID = getattr(settings, 'OSTINATO_PAGES_SITE_TREEID', None)

    ## Some basic page checking and authorization
    if 'path' in kwargs:
        if kwargs['path'][-1] == '/':
            path = kwargs['path'][:-1].split('/')
        else:
            path = kwargs['path'].split('/')

        if PAGES_SITE_TREEID:
            page = get_object_or_404(Page, slug=path[-1], tree_id=PAGES_SITE_TREEID)
        else:
            page = get_object_or_404(Page, slug=path[-1])

    else:
        # If we are looking at the root path, show the root page for the current site
        if PAGES_SITE_TREEID:
            page = get_object_or_404(Page, tree_id=PAGES_SITE_TREEID, level=0)
        else:
            page = get_object_or_404(Page, tree_id=1, level=0)

    sm = get_workflow()(instance=page)
    has_perm = request.user.has_perm('pages.private_view')
    if not request.user.is_superuser and sm.state == 'Private' and not has_perm:
        return http.HttpResponseForbidden()

    content = page.get_content_model()

    ## Check if the page has a custom view
    if hasattr(content.ContentOptions, 'view'):
        module_path, view_class = content.ContentOptions.view.rsplit('.', 1)

        # Import our custom view
        v = __import__(module_path, locals(), globals(), [view_class], -1)\
            .__dict__[view_class]

        if hasattr(v, 'as_view'):
            return v.as_view(page=page)(request, *args, **kwargs)
        else:
            # Doesn't look like this is a class based view. Treat it as a
            # traditional function based view
            kwargs.update({'page': page, 'template': page.get_template()})
            return v(request, *args, **kwargs)

    else:
        return PageView.as_view(page=page)(request, *args, **kwargs)


class PageView(TemplateView):

    page = None

    def get_template_names(self, **kwargs):
        return self.page.get_template()

    def get_context_data(self, **kwargs):
        c = super(PageView, self).get_context_data(**kwargs)
        c['page'] = self.page
        return c


class PageReorderView(View):

    @method_decorator(staff_member_required)
    def post(self, *args, **kwargs):
        form = MovePageForm(self.request.POST)
        if form.is_valid():
            form.save()
        return http.HttpResponseRedirect(
            reverse('admin:ostinato_pages_page_changelist'))


class PageDuplicateView(View):

    @method_decorator(staff_member_required)
    def post(self, *args, **kwargs):
        form = DuplicatePageForm(self.request.POST)
        if form.is_valid():
            new_page = form.save()
            next = reverse('admin:ostinato_pages_page_change',
                           args=(new_page.id,))
        else:
            next = reverse('admin:ostinato_pages_page_changelist')
        return http.HttpResponseRedirect(next)

