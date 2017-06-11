# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import MassNotification
from .tasks import send_mass_push_notification


@admin.register(MassNotification)
class MassNotificationAdmin(admin.ModelAdmin):
    """
    Model admin for ```tandlr.notifications.models.MassNotification``` model.
    """
    actions = None
    date_hierarchy = 'delivery_date'

    list_filter = ('state', )
    list_display = (
        'body',
        'university',
        'delivery_date',
        'state'
    )

    search_fields = ('body', )
    readonly_fields = ('state', )
    fields = ('body', 'delivery_date', 'university')

    def has_change_permission(self, request, obj=None):
        """
        Disables the edition of an instance if it is currently delivered.
        """
        if obj and obj.state == MassNotification.STATE.DELIVERED:
            return False

        return super(MassNotificationAdmin, self).has_change_permission(
            request, obj=obj
        )

    def save_model(self, request, obj, form, changed):
        """
        When an instance's delivery date is changed, then revoke the celery
        task scheduled to send the notification and create a new one scheduled
        to the new delivery date.
        """
        if changed and 'delivery_date' in form.changed_data:
            old_task = send_mass_push_notification.AsyncResult(
                obj.celery_task_id
            )
            old_task.revoke()

            new_task = send_mass_push_notification.apply_async(
                (obj.pk, ), eta=obj.delivery_date
            )
            obj.celery_task_id = new_task.task_id

        super(MassNotificationAdmin, self).save_model(
            request, obj, form, changed
        )

    def delete_model(self, request, obj):
        """
        Before an instance is deleted, revoke the celery task scheduled to
        send the push notification.
        """
        task = send_mass_push_notification.AsyncResult(obj.celery_task_id)
        task.revoke()

        super(MassNotificationAdmin, self).delete_model(request, obj)
