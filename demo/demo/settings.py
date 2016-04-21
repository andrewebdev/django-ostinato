"""
Django settings for demo project.

Generated by 'django-admin startproject' using Django 1.9.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
import ostinato.polyprep


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(04#f3m#e=588929)x_vn)8fu$91rz%=&d2!wmu^)r7t85u#)&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'ostinato.admin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'ostinato',
    'ostinato.pages',
    'ostinato.contentfilters',

    # Other dependencies
    'mptt',
    'taggit',
    # 'taggit_templatetags',

    # Our Website Custom apps
    'demo',
    'website',
    'blog'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'demo.urls'

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
WSGI_APPLICATION = 'demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'demo.db',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-GB'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'

# Send emails to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Ostinato settings
SITE_ID = 1
OSTINATO_PAGES_SITE_TREEID = 1

# Third party app config
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'plugins': "paste",
    'relative_urls': False,
    # 'remove_script_host': False,
    # 'document_base_url': '',

    'theme_advanced_buttons1' : "bold,italic,|,justifyleft,justifycenter,justifyright,justifyfull,bullist,numlist,|,undo,redo,|,link,unlink,code,image,|,formatselect,|,pastetext,",
    'theme_advanced_buttons2' : "",
    'theme_advanced_buttons3' : "",
    'theme_advanced_buttons4' : "",
    'theme_advanced_toolbar_location' : "top",
    'theme_advanced_toolbar_align' : "left",
    'theme_advanced_statusbar_location' : "bottom",
    'theme_advanced_resizing' : True,
    'theme_advanced_blockformats' : "h1,h2,h3,p,blockquote",

    'width': 760,
    'height': 400,

    'paste_strip_class_attributes': 'all',
    'paste_auto_cleanup_on_paste' : True,
    'paste_convert_middot_lists': False,
    'paste_remove_styles' : True,
    'paste_retain_style_properties': '',

    'extended_valid_elements': "a[class|name|href|target|title|onclick|rel],"\
        "script[type|src],"\
        "iframe[src|style|width|height|scrolling|marginwidth|marginheight|frameborder],"\
        "$elements",
}

if 'test' in sys.argv:
    from test_settings import *

