from ostinato.pages.views import PageView
from django.views.generic.detail import DetailView
from django.views.generic.dates import DateDetailView

from ostinato.pages.models import Page
from blog.models import Entry


class LandingPageView(PageView):

    def get_context_data(self, **kwargs):
        c = super(LandingPageView, self).get_context_data(**kwargs)
        num = int(self.page.contents.max_latest_entries)
        c['latest_entries'] = Entry.objects.published()[:num]
        return c


class EntryPreviewView(DetailView):
    model = Entry
    context_object_name = "entry"

    def get_context_data(self, **kwargs):
        c = super(EntryPreviewView, self).get_context_data(**kwargs)
        c['page'] = Page.objects.filter(template="blog.landingpage")[0]
        return c


class EntryDetailView(DateDetailView):
    model = Entry
    date_field = "publish_date"
    year_format = "%Y"
    month_format = "%m"
    day_format = "%d"
    context_object_name = "entry"

    def get_context_data(self, **kwargs):
        c = super(EntryDetailView, self).get_context_data(**kwargs)
        c['page'] = Page.objects.filter(template="blog.landingpage")[0]
        return c

