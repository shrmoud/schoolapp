# -*- coding: utf-8 -*-
from datetime import timedelta

from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils import timezone

from tandlr.notifications.models import Notification
from tandlr.reports.models import (
    ActivitySession,
    NewUser,
    NotificationSent,
    SessionCancelled,
    SessionRegistered,
    SessionSale,
    TopStudentUser,
    TopTeacherUser
)
from tandlr.scheduled_classes.models import ClassBill
from tandlr.users.models import UserSummary

from .actions import export_as_csv


@admin.register(ActivitySession)
class SessionSummaryAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    list_display = ['created_datetime', 'count']

    actions = [export_as_csv]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(SessionSummaryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request):

        qs = super(SessionSummaryAdmin, self).get_queryset(request)

        now = timezone.now()

        one_month_before = now - timedelta(days=30)

        return qs.filter(
            created_datetime__gte=one_month_before
        ).order_by(
            '-count'
        )


@admin.register(SessionRegistered)
class ReportSessionRegistered(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    list_display = [
        'student',
        'teacher',
        'subject',
        'class_status',
        'class_start_date',
        'class_price',
        'class_extra'
    ]

    actions = [export_as_csv]

    list_filter = [
        'class_status'
    ]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReportSessionRegistered, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        return self.model.objects.filter(
            class_start_date__gte=(timezone.now() - timedelta(days=30))
        )

    def class_price(self, obj):
        """
        If the class is in status "ended" print the first bill
        """
        if obj.class_status_id == 5:
            bill = obj.bills.order_by('id').first()
            return bill.subtotal - bill.commission_amount
        return ''

    def class_extra(self, obj):
        """
        If the class is in status "ended" print the total for all the
        extra bills
        """
        if obj.class_status_id == 5:
            total = 0
            for bill in obj.bills.order_by('id').all()[1:]:
                total += bill.subtotal - bill.commission_amount
            return total if total > 0 else '-'
        return ''


@admin.register(SessionCancelled)
class ReportSessionCancelled(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    list_display = [
        'student',
        'teacher',
        'subject',
        'class_status',
        'class_start_date'
    ]

    actions = [export_as_csv]

    list_filter = [
        'class_status'
    ]

    readonly_fields = [
        'teacher',
        'student',
        'subject',
        'class_start_date',
        'class_end_date',
        'class_time',
        'place_description',
        'class_status',
        'class_detail'
    ]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReportSessionCancelled, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        return self.model.objects.filter(
            class_start_date__gte=(timezone.now() - timedelta(days=30)),
            class_status__id=7
        )


@admin.register(NewUser)
class ReportNewUser(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    exclude = [
        'groups',
        'user_permissions'
    ]

    list_display = [
        'email',
        'name',
        'last_name',
        'gender'
    ]

    actions = [export_as_csv]

    list_filter = [
        'is_active',
        'is_teacher',
        'is_student'
    ]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReportNewUser, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        return self.model.objects.filter(
            register_date__gte=(timezone.now() - timedelta(days=30))
        )


@admin.register(TopStudentUser)
class ReportTopCurrentStudent(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    list_per_page = 5

    list_select_related = [
        'user_summary'
    ]

    exclude = [
        'groups',
        'user_permissions'
    ]

    list_display = [
        'name',
        'last_name',
        'sessions_as_student'
    ]

    actions = [export_as_csv]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReportTopCurrentStudent, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request, *args, **kwargs):
        id_top_user_summary = UserSummary.objects.all().order_by(
            '-lessons_as_student'
        ).values('user')[:5]

        return TopStudentUser.objects.filter(
            id__in=id_top_user_summary
        ).order_by(
            '-user_summary__lessons_as_student'
        )


@admin.register(TopTeacherUser)
class ReportTopCurrentTeacher(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    list_per_page = 5

    list_select_related = [
        'user_summary'
    ]

    exclude = [
        'groups',
        'user_permissions'
    ]

    list_display = [
        'name',
        'last_name',
        'sessions_as_teacher'
    ]

    actions = [export_as_csv]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReportTopCurrentTeacher, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request, *args, **kwargs):
        id_top_user_summary = UserSummary.objects.all().order_by(
            '-sessions_as_teacher'
        ).values('user')[:5]

        return TopTeacherUser.objects.filter(
            id__in=id_top_user_summary
        ).order_by(
            '-user_summary__sessions_as_teacher'
        )


@admin.register(NotificationSent)
class ReportSentNotifications(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    list_display = [
        'notifications_sent_in_last_period'
    ]

    actions = [export_as_csv]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReportSentNotifications, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request, *args, **kwargs):
        return Notification.objects.filter(
            id__in=[1]
        )


@admin.register(SessionSale)
class ReportSessionSales(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    list_per_page = 31

    list_select_related = [
        'session'
    ]

    list_display = [
        'session',
        'hourly_price',
        'duration',
        'was_paid',
        'student',
        'teacher',
        'subtotal'
    ]

    actions = [export_as_csv]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReportSessionSales, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self, request, *args, **kwargs):
        return ClassBill.objects.filter(
            created_at__gte=(timezone.now() - timedelta(days=30)),
            was_paid=True
        )
