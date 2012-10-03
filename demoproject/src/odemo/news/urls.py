from django.conf.urls import patterns, include, url
from django.views.generic import DetailView

from odemo.news.models import NewsItem


urlpatterns = patterns('',

    url(r'^(?P<pk>\d+)/$', DetailView.as_view(model=NewsItem),
        name='newsitem_detail'),

)
