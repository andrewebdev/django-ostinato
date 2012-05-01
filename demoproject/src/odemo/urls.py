from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import DetailView

from odemo.news.models import NewsItem
from odemo.news.views import NewsPageView

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^news/(?P<id>\d+)/$', DetailView.as_view(model=NewsItem),
        name='newsitem_detail'),
    
    url(r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),

)


urlpatterns += staticfiles_urlpatterns()


urlpatterns += patterns('',
    url(r'^', include('ostinato.pages.urls')),
)
