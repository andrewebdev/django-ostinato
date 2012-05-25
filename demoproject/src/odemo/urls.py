from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import DetailView

from ostinato.pages.registry import page_content
from odemo.news.models import NewsItem
from odemo.news.views import NewsPageView

admin.autodiscover()
page_content.autodiscover()


urlpatterns = patterns('',
    url(r'^news/(?P<pk>\d+)/$', DetailView.as_view(model=NewsItem),
        name='newsitem_detail'),
    
    (r'^ckeditor/', include('ckeditor.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
    # (r'^grappelli/', include('grappelli.urls')),

)


urlpatterns += staticfiles_urlpatterns()


urlpatterns += patterns('',
    url(r'^', include('ostinato.pages.urls')),
)
