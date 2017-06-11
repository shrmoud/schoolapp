# -*- coding: utf-8 -*-
from . import tasks


def send_push_notification_on_creation(sender, instance, created, **kwargs):
    """
    Sends a push notification to the receiver's active devices asyncronouslly
    when a ```tandlr.notifications.model.Notification``` is created.
    """
    if created and instance.receiver.settings.push_notifications_enabled:
        tasks.send_push_notification.apply_async((instance.pk, ))


def schedule_push_notification_delivery(sender, instance, created, **kwargs):
    """
    Creates a new celery task to actually perform the a mass notification
    delivery scheduled to the given instance's delivery date only when an
    instance is created.
    """
    if created:
        task = tasks.send_mass_push_notification.apply_async(
            (instance.pk, ), eta=instance.delivery_date
        )

        instance.celery_task_id = task.task_id
        instance.save()
