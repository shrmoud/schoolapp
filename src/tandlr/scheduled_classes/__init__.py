# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import timedelta

from django.conf import settings


default_app_config = 'tandlr.scheduled_classes.apps.ScheduledClassesConfig'


if not settings.CELERYBEAT_SCHEDULE:

    settings.CELERYBEAT_SCHEDULE = {
        #
        # Excecutes every 4 hours the tasks to check the sessions
        #
        'check_sessions': {
            'task': 'tandlr.scheduled_classes.tasks.check_sessions',
            'schedule': timedelta(hours=4)
        }

    }

elif settings.CELERYBEAT_SCHEDULE:

    settings.CELERYBEAT_SCHEDULE.update(
        {
            #
            # Excecutes every 4 hours the tasks to check the sessions
            #
            'check_sessions': {
                'task': 'tandlr.scheduled_classes.tasks.check_sessions',
                'schedule': timedelta(hours=4)
            }
        }
    )
