from django.db import models

from ostinato.pages.models import PageContent, ContentMixin


class NewsItem(models.Model):

    title = models.CharField(max_length=150)
    content = models.TextField()
    publish_date = models.DateTimeField()

    def __unicode__(self):
        return '%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('newsitem_detail', [self.id])


## Create a News List page
class NewsListPageContent(ContentMixin, PageContent):
    ## We could store some information here, like how many items we want
    ## to show on the page.

    class ContentOptions:
        template = 'page_templates/news_list_page.html'
        view = 'odemo.news.views.NewsPageView'


class PageWithNews(ContentMixin, PageContent):
    """
    A normal page with some content, but also contains a link to a specific
    news item.
    """
    news_item = models.ForeignKey(NewsItem)

    class ContentOptions:
        template = 'page_templates/news_page.html'
        
