"""
Django settings for booking project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.core.urlresolvers import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$qj!v#@&dw1(8-4=io*$u#!3_&2*8q3cf#4p$i*yh6%*a2smu7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEMO = True

ALLOWED_HOSTS = []

LOGIN_URL = reverse_lazy("authentication:login")
LOGIN_REDIRECT_URL = reverse_lazy("events:calendar")

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MAPBOX_TOKEN = ''
GOOGLE_MAPS_API_KEY = ''

# Application definition

INSTALLED_APPS = (
    'authentication',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',
    'activities',
    'events',
    'news',
    'rooms',
    'base',
    'brochure.apps.BrochureConfig',
    'attendances'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'base.middleware.BookingRemoteUserMiddleware',
)

AUTHENTICATION_BACKENDS = [
    'base.backends.BookingRemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'booking.urls'

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
                'django.template.context_processors.i18n',
                'base.context_processors.demo',
                'base.context_processors.waiting_events_counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'booking.wsgi.application'

SESSION_COOKIE_AGE = 432000

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.9,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'it-it'
DATE_FORMAT = '%d/%m/%Y'
SHORT_DATE_FORMAT = '%d/%m/%Y'
DATE_INPUT_FORMATS = ['%d/%m/%Y']
TIME_ZONE = 'Europe/Rome'

TIME_FORMAT = "%H:%M"
TIME_INPUT_FORMATS = [
    '%H:%M:%S',     # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M',        # '14:30'
    '%H',           # '14'
]

USE_I18N = True

USE_L10N = False

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, app, 'locale') for app in (
        'activities',
        'events',
        'news',
        'rooms',
        'base',
    )
]

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

BACKUP_COMMAND = None

# Logging
# http://ianalexandr.com/blog/getting-started-with-django-logging-in-5-minutes.html
# https://stackoverflow.com/questions/5739830/simple-log-to-file-example-for-django-1-3

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'booking': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# Use django-nose to run tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Override using local (production) settings
try:
    from booking.local_settings import *
except ImportError as e:
    import logging
    log = logging.getLogger(__name__)
    log.warning("Could not load local_settings. %s", e)
