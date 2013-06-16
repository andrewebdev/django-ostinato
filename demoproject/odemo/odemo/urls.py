from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from ostinato.pages.registry import page_templates


admin.autodiscover()
page_templates.autodiscover()


urlpatterns = patterns('',
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
    (r'^tinymce/', include('tinymce.urls')),
)

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('', url(r'^', include('ostinato.pages.urls')),)
