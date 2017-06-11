# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import timedelta

from django.conf import settings

unpaid_session_sales = {
    # Executes every 14 days
    'unpaid_session_sales': {
        'task': 'tandlr.reports.tasks.unpaid_session_sales',
        'schedule': timedelta(days=settings.REPORT_TIMESPAN),
    }
}

if not settings.CELERYBEAT_SCHEDULE and settings.PRODUCTION:

    settings.CELERYBEAT_SCHEDULE = unpaid_session_sales

elif settings.CELERYBEAT_SCHEDULE and settings.PRODUCTION:

    settings.CELERYBEAT_SCHEDULE.update(unpaid_session_sales)
