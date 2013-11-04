from django.conf import settings

OSTINATO_PAGES_SETTINGS = getattr(settings, 'OSTINATO_PAGES_SETTINGS', {})
PAGES_SETTINGS = {
    'CACHE_NAME': 'default',
    'DEFAULT_STATE': 5,
}
PAGES_SETTINGS.update(OSTINATO_PAGES_SETTINGS)
