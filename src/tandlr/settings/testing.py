# -*- coding: utf-8 -*-
"""
Django testing settings for tandlr project.
"""
from distutils.version import LooseVersion
from subprocess import check_output

from . import *  # noqa


# Short key for tests speed up
SECRET_KEY = 'secret'


# Debug
DEBUG = False

TEMPLATE_DEBUG = DEBUG


# Application definition
INSTALLED_APPS += (
    'kombu.transport.django',
)


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'tandlr.sqlite',
    },
}


spatialite_version = check_output(
    "spatialite tandlr.sqlite 'SELECT spatialite_version()'",
    shell=True
).strip()


if LooseVersion(spatialite_version) >= LooseVersion("4.2"):
    SPATIALITE_LIBRARY_PATH = 'mod_spatialite'


# Simple password hasher for tests speed up
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


# Celery
BROKER_URL = 'django://'


# Email, dummy backend for tests speed up
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

STRIPE_PRIVATE_KEY = 'sk_test_cs9VK3yKc7ZqZ8VuDX9HYFCi'

STRIPE_PUBLIC_KEY = 'pk_test_lqiPxVBtth4BkrapFDojtcvQ'
