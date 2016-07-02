from django.conf.urls import url


urlpatterns = [
    url(r'^(?P<browser_id>[-\w]+)$',
        'ostinato.contentbrowser.views.browser_dispatch',
        name="ostinato_contentbrowser_browser"),
]
