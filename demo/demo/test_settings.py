
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'ostinato',
    'ostinato.pages',
    # 'ostinato.contentfilters',
    # Only really adding these so that we can run test against them
    # 'ostinato.statemachine',

    # Other dependencies
    'mptt',
]

