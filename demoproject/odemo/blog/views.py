from ostinato.pages.views import PageView

from blog.models import Entry


class LandingPageView(PageView):

    def get_context_data(self, **kwargs):
        c = super(LandingPageView, self).get_context_data(**kwargs)
        num = int(self.page.contents.max_latest_entries)
        c['latest_entries'] = Entry.objects.published()[:num]
        return c