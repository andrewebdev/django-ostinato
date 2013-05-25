from django.conf.urls import patterns, url

from ostinato.pages.views import page_dispatch, PageReorderView, PageDuplicateView


urlpatterns = patterns('',
    url(r'^$', page_dispatch, name='ostinato_page_home'),

    url(r'^page_reorder/$', PageReorderView.as_view(),
        name='ostinato_page_reorder'),

    url(r'^page_duplicate/$', PageDuplicateView.as_view(),
        name='ostinato_page_duplicate'),

    # This must be last
    url(r'^(?P<path>.*)/$', page_dispatch, name='ostinato_page_view'),
)
