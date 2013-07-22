from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # (r'^grappelli/', include('grappelli.urls')),
    (r'^tinymce/', include('tinymce.urls')),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns('', url(r'^', include('ostinato.pages.urls')))
