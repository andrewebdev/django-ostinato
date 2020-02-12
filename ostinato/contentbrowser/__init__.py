import os
from django.conf import settings

import warnings
warnings.warn(
    "ContentBrowser app have been deprecated and will be replaced with a "
    "better text editor.",
    DeprecationWarning)

default_app_config = 'ostinato.contentbrowser.apps.OstinatoContentBrowserConfig'

OSTINATO_CONTENTBROWSER = getattr(settings, 'OSTINATO_CONTENTBROWSER', {})
CONTENTBROWSER = {
    'browsers': [],
}
CONTENTBROWSER.update(OSTINATO_CONTENTBROWSER)
