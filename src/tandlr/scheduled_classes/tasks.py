# -*- coding: utf-8 -*-
from datetime import timedelta

from celery import task

from django.utils import timezone

from tandlr.scheduled_classes.models import Class


@task
def check_sessions():
    """
    Reviews all the sessions in state "on course" (4) and the one that haven't
    been closed in the last 4 hours are moved into state "finish" (5)
    """
    now = timezone.localtime(timezone.now())

    for session in Class.objects.filter(
        class_status_id=4,
        class_start_date__lte=(now - timedelta(hours=4))
    ):
        session.class_status_id = 5
        session.save()
