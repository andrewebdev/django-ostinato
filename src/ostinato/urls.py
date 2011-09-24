from django.conf.urls.defaults import patterns, include, url

from ostinato.views import ContentItemEdit

urlpatterns = patterns('',
    url(r'^contentitem/edit/(?P<id>\d+)/$', ContentItemEdit.as_view(),
        name="ostinato_contentitem_edit"),
)