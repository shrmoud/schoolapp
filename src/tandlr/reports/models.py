# -*- coding: utf-8 -*-
from django.db import models

from tandlr.notifications.models import Notification
from tandlr.scheduled_classes.models import (
    Class,
    ClassBill
)
from tandlr.users.models import User


class BaseConfigurationReport(models.Model):
    """
    Abstract model, that model brings a property for returning
    model fields and name report
    """

    fields_report = []
    name_report = ''

    @property
    def get_fields_report(self):
        return self.fields_report

    @property
    def get_name_report(self):
        return self.name_report

    class Meta:
        abstract = True


class SessionSummary(models.Model):
    """
    Created model SessionSummary for reports in Tandlr.
    """
    created_datetime = models.DateTimeField()
    count = models.IntegerField(default=1)


class ActivitySession(BaseConfigurationReport, SessionSummary):

    class Meta:
        proxy = True
        verbose_name_plural = "Sessions activity"
        verbose_name = "Session activity"

    name_report = 'report_top_view'
    fields_report = [
        'created_datetime',
        'count'
    ]


class SessionRegistered(BaseConfigurationReport, Class):

    class Meta:
        proxy = True
        verbose_name_plural = "Sessions registered"
        verbose_name = "Session registered"

    name_report = 'report_sessions_registered'
    fields_report = [
        'student',
        'teacher',
        'subject',
        'class_status',
        'class_start_date'
    ]


class SessionCancelled(BaseConfigurationReport, Class):

    class Meta:
        proxy = True
        verbose_name_plural = "Sessions cancelled"
        verbose_name = "Session cancelled"

    name_report = 'report_sessions_cancelled'
    fields_report = [
        'student',
        'teacher',
        'subject',
        'class_status',
        'class_start_date'
    ]


class NewUser(BaseConfigurationReport, User):

    class Meta:
        proxy = True
        verbose_name_plural = "New users"
        verbose_name = "New user"

    name_report = 'report_new_users'
    fields_report = [
        'name',
        'last_name',
        'gender',
        'email'
    ]


class TopStudentUser(BaseConfigurationReport, User):

    class Meta:
        proxy = True
        verbose_name_plural = "Top students user"
        verbose_name = "Top student user"

    name_report = 'report_top_5_as_student'
    fields_report = [
        'name',
        'last_name',
        'sessions_as_student'
    ]


class TopTeacherUser(BaseConfigurationReport, User):

    class Meta:
        proxy = True
        verbose_name_plural = "Top teachers user"
        verbose_name = "Top teacher user"

    name_report = 'report_top_5_as_teacher'
    fields_report = [
        'name',
        'last_name',
        'sessions_as_teacher'
    ]


class NotificationSent(BaseConfigurationReport, Notification):

    class Meta:
        proxy = True
        verbose_name_plural = "Notifications sent"
        verbose_name = "Notification sent"

    name_report = 'report_notifications_sent'
    fields_report = [
        'notifications_sent_in_last_period'
    ]


class SessionSale(BaseConfigurationReport, ClassBill):

    class Meta:
        proxy = True
        verbose_name_plural = "Sessions sale"
        verbose_name = "Session sale"

    name_report = 'report_sales_sessions'
    fields_report = [
        'session',
        'hourly_price',
        'number_of_hours',
        'was_paid',
        'student',
        'teacher',
        'subtotal'
    ]
