from django.conf.urls import patterns, include, url

from ostinato.pages.views import PageView


urlpatterns = patterns('',
    url(r'^$', PageView.as_view(), name="ostinato_page_home"),

    # This must be last
    url(r'^(?P<path>.*)/$', PageView.as_view(), name="ostinato_page_view"),
)


