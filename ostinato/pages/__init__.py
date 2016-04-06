from django.conf import settings

default_app_config = 'ostinato.pages.apps.OstinatoPagesConfig'

OSTINATO_PAGES_SETTINGS = getattr(settings, 'OSTINATO_PAGES_SETTINGS', {})
PAGES_SETTINGS = {
    'CACHE_NAME': 'default',
    'DEFAULT_STATE': 5,
}
PAGES_SETTINGS.update(OSTINATO_PAGES_SETTINGS)

