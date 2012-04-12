from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from ostinato.pages.models import Page
from ostinato.pages.utils import get_template_by_id

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
            # If we are looking at the root object, show the root page
            c['current_page'] = get_object_or_404(Page, lft=1)

        self.template_name = get_template_by_id(
                c['current_page'].template)['template']

        # Determine the zones and add this to the context
        c['page_zones'] = {}

        for zone in c['current_page'].get_zones():
            c['page_zones'].update({zone.zone_id: zone})

        return c

