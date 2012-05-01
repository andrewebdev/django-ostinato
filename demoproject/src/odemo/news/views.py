from ostinato.pages.views import PageView

from odemo.news.models import NewsItem


class NewsPageView(PageView):

    def get_context_data(self, **kwargs):
        c = super(NewsPageView, self).get_context_data(**kwargs)
        c['latest_news'] = NewsItem.objects.all()[:10]
        return c
