# -*- coding: utf-8 -*-
from django.db import models

from tandlr.users.models import User


class LogbookUser(models.Model):
    """
    Mapping table logbook_user in Tandlr,
    register activities users.
    """
    user = models.ForeignKey(
        User,
        null=False
    )
    activity = models.TextField(
        max_length=45,
        blank=True,
        null=True
    )
    module = models.TextField(
        max_length=45,
        blank=True,
        null=True
    )
    body_log = models.CharField(
        max_length=1000,
        blank=True,
        null=True
    )

    # The DEBUG Level designates fine-grained informational
    # events that are most useful to debug an application.

    DEBUG = 'DEBUG'

    # The ERROR level designates error events that might
    # still allow the application to continue running.

    ERROR = 'ERROR'

    # The INFO level designates informational messages that highlight
    # the progress of the application at coarse-grained level.

    INFO = 'INFO'

    LOG_LEVEL = (
        (DEBUG, 'DEBUG'),
        (ERROR, 'ERROR'),
        (INFO, 'INFO'),
    )

    log_level = models.CharField(
        max_length=5,
        choices=LOG_LEVEL,
        default=INFO
    )

    logbook_date = models.DateField(
        auto_now=True
    )

    class Meta:
        db_table = 'logbook_user'


class LogMail(models.Model):
    """
    Mapping table log_mail, register delivery mails in Tandlr.
    """
    user = models.ForeignKey(
        User,
        null=False
    )
    mail_from = models.TextField(
        max_length=45,
        blank=False,
        null=False
    )
    mail_subject = models.TextField(
        max_length=50,
        blank=False,
        null=False
    )

    mail_sent_date = models.DateField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'log_mail'
