from django.urls import path
from ostinato.contentbrowser.views import browser_dispatch


import warnings
warnings.warn(
    "ContentBrowser app have been deprecated and will be replaced with a "
    "better text editor.",
    DeprecationWarning)


urlpatterns = [
    path(
        '<str:browser_id>',
        browser_dispatch,
        name="ostinato_contentbrowser_browser"
    ),
]
