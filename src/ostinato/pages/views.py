from django.views.generic import View, TemplateView
from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404
from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django import http

from ostinato.pages.models import Page
from ostinato.pages.forms import MovePageForm
from ostinato.pages.utils import get_template_by_name


class PageView(TemplateView):

    model = Page

    def get_context_data(self, **kwargs):
        c = super(PageView, self).get_context_data(**kwargs)

        if 'path' in kwargs:
            path = kwargs['path'].split('/')

            if not path[-1]:
                path = path[:-1]

            c['current_page'] = get_object_or_404(Page, slug=path[-1])

        else:
            # If we are looking at the root object, show the first root page
            c['current_page'] = Page.tree.root_nodes()[0]

        self.template_name = get_template_by_name(
                c['current_page'].template)['template']

        # Determine the zones and add this to the context
        c['page_zones'] = {}

        for zone in c['current_page'].get_zones():
            c['page_zones'].update({zone.zone_id: zone})

        return c


    def get(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)

        if c['current_page'].sm.state == 'private':
            if c['current_page'].author != self.request.user or\
                    not self.request.user.is_superuser:
                return http.HttpResponseForbidden()

        return self.render_to_response(c)


class PageReorderView(View):

    def post(self, *args, **kwargs):
        form = MovePageForm(self.request.POST)

        if form.is_valid():
            form.save()

        return http.HttpResponseRedirect(reverse('admin:pages_page_changelist'))


