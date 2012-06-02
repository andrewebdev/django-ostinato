from django.db import models
from django.utils import timezone

from ostinato.pages.models import PageContent
from ostinato.statemachine.core import State, StateMachine

from odemo.models import CKContentMixin


## A custom statemachine for news items
class Private(State):
    verbose_name = 'Private'
    transitions = {'publish': 'public'}

    def publish(self, **kwargs):
        if self.instance:
            self.instance.publish_date = timezone.now()


class Public(State):
    verbose_name = 'Public'
    transitions = {'retract': 'private', 'archive': 'archived'}

    def retract(self, **kwargs):
        if self.instance:
            self.instance.publish_date = None


class Archived(State):
    verbose_name = 'Archived'
    transitions = {}

class NewsWorkflow(StateMachine):
    state_map = {'private': Private, 'public': Public, 'archived': Archived}
    initial_state = 'private'


## Our News Item model
class NewsItem(models.Model):

    title = models.CharField(max_length=150)
    content = models.TextField()
    publish_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=50, default='private')

    def __unicode__(self):
        return '%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('newsitem_detail', [self.id])


## Create a News List page
class NewsListPageContent(CKContentMixin):
    ## We could store some information here, like how many items we want
    ## to show on the page.

    class ContentOptions:
        template = 'page_templates/news_list_page.html'
        view = 'odemo.news.views.NewsPageView'


class PageWithNews(CKContentMixin):
    """
    A normal page with some content, but also contains a link to a specific
    news item.
    """
    news_item = models.ForeignKey(NewsItem)

    class ContentOptions:
        template = 'page_templates/news_page.html'
        
