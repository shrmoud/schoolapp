# -*- coding: utf-8 -*-
"""
Django production settings for tandlr project.
"""
from .staging import *  # noqa

PRODUCTION = True
#
# The report timespan variable is used to assign the amount of days
# that are going to be covered by the report
#
REPORT_TIMESPAN = 14

# Frontend urls
FRONTEND_BASE_HOST = "https://booking.tandlr.info"
FRONTEND_RECOVERY_PASSWORD_URL = "{}{}".format(
    FRONTEND_BASE_HOST,
    "/#/change-password/"
)

ALLOWED_HOSTS = [
    'tandlr.info'
]

# CORS headers configuration
CORS_ORIGIN_WHITELIST = (
    'booking.tandlr.info',
)


REPORT_EMAILS = ['pablo@tandlr.com']
BCC_REPORT_EMAILS = ['alberto.jimenez@vincoorbis.com']
