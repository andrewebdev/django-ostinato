
SECRET_KEY = 'fake-key'

ROOT_URLCONF = 'ostinato.tests.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'ostinato',

    # Pages
    'ostinato.tests.pages',
    'ostinato.pages',
    'ostinato.tests.blog',
    'ostinato.contentfilters',
    'ostinato.medialib',
    # 'ostinato.contentbrowser',
    # 'ostinato.statemachine',

    # Other dependencies
    'mptt',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_URL = '/static/'

# ContentBrowser Settings
OSTINATO_CONTENTBROWSER = {
    'browsers': [
        'ostinato.tests.contentbrowser.views.SampleBrowser',
    ],
}

