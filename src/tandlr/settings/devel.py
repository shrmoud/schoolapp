# -*- coding: utf-8 -*-
"""
Django development settings for tandlr project.
"""
import os

from . import *  # noqa


# Debug
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    '0.0.0.0:8000',
]

REPORT_EMAILS = ['test@tandlr.com']

# Application definition
INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'tandlr',
        'USER': 'vagrant'
    }
}


# Celery
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

CELERY_RESULT_BACKEND = BROKER_URL


# Debug toolbar
INTERNAL_IPS = ('10.0.2.2',)

GRAPH_MODELS = {
}


# APNs
APNS_USE_SANDBOX = True

APNS_CERT_FILE_PATH = os.path.realpath(os.path.join(
    BASE_DIR, '..', '..', 'certs', 'ck.pem'
))

STRIPE_PRIVATE_KEY = 'sk_test_cs9VK3yKc7ZqZ8VuDX9HYFCi'

STRIPE_PUBLIC_KEY = 'pk_test_lqiPxVBtth4BkrapFDojtcvQ'
