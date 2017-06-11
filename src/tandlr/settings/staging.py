# -*- coding: utf-8 -*-
"""
Django staging settings for tandlr project.
"""
import os
import urlparse

from decimal import Decimal

from . import *  # noqa


DEBUG = False

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'tandlr.pythonballz.com',
]


# Application definition
INSTALLED_APPS += (
    'opbeat.contrib.django',
)

MIDDLEWARE_CLASSES += (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
)


# Database settings
urlparse.uses_netloc.append('postgres')
url = urlparse.urlparse(os.environ['DATABASE_URL'])

DATABASES = {
    'default': {
        'ENGINE': {
            'postgres': 'django.contrib.gis.db.backends.postgis'
        }[url.scheme],
        'NAME': url.path[1:],
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port
    }
}


# Static files and uploads
MEDIA_ROOT = os.path.realpath(os.path.join(
    os.environ['DATA_DIR'], 'uploads'))

STATIC_ROOT = os.path.realpath(os.path.join(
    os.environ['DATA_DIR'], 'assets'))

MEDIA_URL = '/media/'

STATIC_URL = '/static/'


# Celery with RabbitMQ
if 'AMQP_URL' in os.environ:
    BROKER_URL = os.environ['AMQP_URL']

    CELERY_RESULT_BACKEND = BROKER_URL

    BROKER_TRANSPORT_OPTIONS = {
        'fanout_prefix': True,
        'fanout_patterns': True,
    }


# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ['EMAIL_HOST']

EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']

EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']

EMAIL_PORT = int(os.environ['EMAIL_HOST_PORT'])

EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS'] == 'True'

DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']


# APNs
APNS_USE_SANDBOX = os.environ['APNS_USE_SANDBOX'] == 'True'

APNS_CERT_FILE_PATH = os.environ['APNS_CERT_FILE_PATH']

if 'APNS_KEY_FILE_PATH' in os.environ:
    APNS_KEY_FILE_PATH = os.environ['APNS_KEY_FILE_PATH']


# Opbeat
OPBEAT = {
    'ORGANIZATION_ID': os.environ['OPBEAT_ORGANIZATION_ID'],
    'APP_ID': os.environ['OPBEAT_APP_ID'],
    'SECRET_TOKEN': os.environ['OPBEAT_SECRET_TOKEN'],
    'INSTRUMENT_DJANGO_MIDDLEWARE': True,
}


# Stripe
STRIPE_PRIVATE_KEY = os.environ.get('STRIPE_PRIVATE_KEY')

STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')

DEFAULT_CLASS_PRICE_PER_HOUR = Decimal(
    os.environ.get('DEFAULT_CLASS_PRICE_PER_HOUR', '40.00')
)

# CORS headers configuration
CORS_ORIGIN_WHITELIST = (
    '127.0.0.1:3000',
    'localhost:3000',
    'tandlr.vincoorbisdev.com',
    'tandlr.frontendvo.com'
)

# DJANGO CHANNELS CONFIGURATION
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                os.environ.get('REDIS_URL'),
            ],
        },
        "ROUTING": "tandlr.notifications.routing.channel_routing",
    },
}

REPORT_EMAILS = [
    'fernanda@mellow.cc',
    'pablo@tandlr.com'
]

BCC_REPORT_EMAILS = [
    'aa@vincoorbis.com',
    'alberto.jimenez@vincoorbis.com',
]
