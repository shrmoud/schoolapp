# -*- coding: utf-8 -*-
"""
Django settings for tandlr project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from __future__ import absolute_import

import datetime
import os

from decimal import Decimal

from celery.schedules import crontab


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*p_&!3^v6@n_&wy7l_ewpe3e-6cxg@qa-38hw9uu=k=w7f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Authentication
AUTH_USER_MODEL = 'users.User'

# Application definition
INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tandlr',
    'tandlr.users',
    'tandlr.api',
    'tandlr.balances',
    'tandlr.catalogues',
    'tandlr.registration',
    'tandlr.authentication',
    'tandlr.chat',
    'tandlr.feedbacks',
    'tandlr.logs',
    'tandlr.notifications',
    'tandlr.notifications.push.apple',
    'tandlr.payments',
    'tandlr.promotions',
    'tandlr.reports',
    'tandlr.scheduled_classes',
    'tandlr.security_configuration',
    'tandlr.stripe',
    'tandlr.emails',
    # Third party apps
    'django_extensions',
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'django.contrib.gis',
    'channels',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


ROOT_URLCONF = 'tandlr.urls'

WSGI_APPLICATION = 'tandlr.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

CELERY_TIME_ZONE = TIME_ZONE

REPORTS_ROOT = os.path.realpath(
    os.path.join(BASE_DIR, '..', '..', 'media', 'reports')
)

REPORT_EMAILS = ['test@tandlr.com']
BCC_REPORT_EMAILS = []

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    os.path.realpath(os.path.join(BASE_DIR, '..', 'assets')),
)

# Frontend urls
FRONTEND_BASE_HOST = "https://tandlr.vincoorbisdev.com"
FRONTEND_RECOVERY_PASSWORD_URL = "{}{}".format(
    FRONTEND_BASE_HOST,
    "/#/change-password/"
)

STATIC_URL = '/static/'

STATIC_ROOT = os.path.realpath(
    os.path.join(BASE_DIR, '..', '..', 'media', 'assets')
)

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.realpath(
    os.path.join(BASE_DIR, '..', '..', 'media', 'uploads')
)


# Template directories
# See https://docs.djangoproject.com/en/1.7/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    os.path.realpath(os.path.join(BASE_DIR, '..', 'templates')),
)

TEMPLATE_LOADERS = (
    'admin_tools.template_loaders.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)


# Celery
CELERYBEAT_SCHEDULE = {
    'clear-ios-devices-everyday': {
        'task': 'tandlr.notifications.push.apple.tasks'
                '.disable_failed_ios_devices',
        'schedule': crontab(minute=0, hour=0)
    }
}


# Email
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

EMAIL_FILE_PATH = os.path.realpath(os.path.join(
    BASE_DIR, '..', '..', 'media', 'email'
))

DEFAULT_FROM_EMAIL = 'Desarrollo <pruebas@vincoorbis.com>'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.PageNumberPagination',
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 50
}


# FEEDBACK MINIMUM SCORE is  minimum value
# in score that should be take for get average.
FEEDBACK_MINIMUN_SCORE = 1.0

# String representation of money format.
MONEY_QUANTIZE_FORMAT = '0.00'

# Defines the default class price per hour, for all classes in tandlr.
DEFAULT_CLASS_PRICE_PER_HOUR = Decimal('40.00')

CORS_ORIGIN_ALLOW_ALL = True


# JWT_AUTH for jwt
JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'VJWT_ALGORITHM': 'HS256',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=30),
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=360),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

}

# SWAGGER_SETTINGS
SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '1.0',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    'api_key': '',
    'is_authenticated': False,
    'is_superuser': False,
    'permission_denied_handler': None,
    'resource_access_handler': None,
    'info': {
        'contact': 'gp@vincoorbis.com',
        'description': '',
        'license': 'Apache 2.0',
        'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
        'termsOfServiceUrl': 'http://helloreverb.com/terms/',
        'title': 'Tandlr API REST',
    },
    'doc_expansion': 'none',
}

# CORS headers configuration
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = ()


# DJANGO CHANNELS CONFIGURATION
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                'redis://127.0.0.1:6379'
            ],
        },
        "ROUTING": "tandlr.notifications.routing.channel_routing",
    },
}

#
# Flag used to know if we are in production environment
#
PRODUCTION = False

#
# The report timespan variable is used to assign the amount of days
# that are going to be covered by the report
#
REPORT_TIMESPAN = 2
