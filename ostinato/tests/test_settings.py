
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

    # Pages
    'ostinato.tests.pages',
    'ostinato.pages',
    'ostinato.statemachine',
    'ostinato.tests.statemachine_tests',
    'ostinato.tests.blog',
    'ostinato.contentfilters',
    'ostinato.medialib',
    'ostinato.tests.medialib_tests',

    # Other dependencies
    'mptt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'

OSTINATO_PAGES = {
    'templates': {
        'pages.landingpage': {
            'label': 'Landing Page',
            'template': 'pages/landing_page.html',
        },

        'pages.basicpage': {
            'label': 'Basic Page',
            'template': 'pages/basic_page.html',
            'view': 'ostinato.tests.pages.views.CustomView',
            'admin_form': 'ostinato.tests.pages.admin.BasicPageAdminForm',
            'page_inlines': [
                'ostinato.tests.pages.models.ContributorInline',
            ]
        },

        'pages.basicpagefunc': {
            'label': 'Basic Page Func',
            'template': 'pages/basic_page.html',
            'view': 'ostinato.tests.pages.views.functionview'
        },

        'pages.otherpage': {
            'label': 'Some Other Page',
        },
    }
}

OSTINATO_CONTENTBROWSER = {
    'browsers': [
        'ostinato.tests.contentbrowser.views.SampleBrowser',
    ],
}

