from django.conf.urls import patterns, include, url

from ostinato.pages.views import PageView, PageReorderView


urlpatterns = patterns('',
    url(r'^$', PageView.as_view(), name='ostinato_page_home'),

    url(r'^page_reorder/$', PageReorderView.as_view(),
        name='ostinato_page_reorder'),

    # This must be last
    url(r'^(?P<path>.*)/$', PageView.as_view(), name='ostinato_page_view'),
)

