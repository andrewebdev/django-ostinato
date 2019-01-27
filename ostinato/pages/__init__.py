from django.conf import settings

default_app_config = 'ostinato.pages.apps.OstinatoPagesConfig'

OSTINATO_PAGES_SETTINGS = getattr(settings, 'OSTINATO_PAGES', {})
PAGES_SETTINGS = {
    'cache_name': 'default',
    'cache_key_separator': ':',
    'default_state': 'public',
    'workflow_class': 'ostinato.pages.workflow.PageWorkflow',
}
PAGES_SETTINGS.update(OSTINATO_PAGES_SETTINGS)


def get_cache_key(*path):
    key_path = ('ostinato', 'pages') + path
    return PAGES_SETTINGS['cache_key_separator'].join(key_path)
