# -*- coding: utf-8 -*-
from celery import shared_task

from channels import Group

from django.utils import timezone

from tandlr.users.models import DeviceUser

from .push.apple import tasks as apple


@shared_task
def send_push_notification(notification_id):
    """
    Sends push notifications to the receiver's active devices.

    Params:
        notification (Notification): The notification instance that will be
            sent to the devices.

    Returns:
        None
    """
    from .models import Notification

    notification = Notification.objects.get(id=notification_id)
    kwargs = {
        'is_active': True,
        'device_os': 'iOS'
    }

    # Send web notifications
    response_data = (
        '{{"target_id":"{}","target_type":"{}","target_action":"{}"}}'
    ).format(
        str(notification.target_id),
        str(notification.target._meta.model_name),
        str(notification.target_action)
    )

    #
    # Send web notification to specific user.
    #
    Group('notifications' + str(notification.receiver.id)).send({
        'text': response_data
    })

    #
    # Send mobile notifications
    #
    receiver = notification.receiver
    unread_count = receiver.notifications.filter(is_read=False).count()

    extra = {
        'target_id': notification.target_id,
        'target_type': notification.target._meta.model_name,
        'target_action': notification.target_action
    }

    ios_devices = notification.receiver.devices.exclude(
        device_user_token__isnull=True
    ).filter(
        **kwargs
    )

    if ios_devices.exists():
        notifications = []

        for device in ios_devices:
            data = {
                'token': device.device_user_token,
                'alert': notification.body,
                'Badge': unread_count
            }
            data.update(extra)
            notifications.append(data)

        apple.send_push_notifications_multiple(notifications)

    notification.was_delivered = True
    notification.save()


@shared_task
def send_mass_push_notification(notification_id):
    """
    Perform the delivery of a
    ```tandlr.notifications.models.MassNotification``` instance.
    """
    from .models import MassNotification

    notification = MassNotification.objects.get(id=notification_id)
    kwargs = {
        'is_active': True,
        'device_os': 'iOS'
    }

    # Send web notifications
    response_data = '{{"target_action":"{}","message":"{}"}}'.format(
        str("mass_notification"),
        str(notification.body)
    )

    if notification.university_id:
        #
        # Send web mass notification to users of an specific university.
        #
        Group('mass-notifications' + str(notification.university_id)).send({
            'text': response_data
        })
    else:
        #
        # Send mass notifications when this do not have a university registered
        #
        Group('mass-notifications').send({'text': response_data})

    #
    # Send mobile notifications
    #
    if notification.university:
        kwargs.update(user__university=notification.university)

    ios_devices = DeviceUser.objects.exclude(
        device_user_token__isnull=True
    ).filter(
        **kwargs
    ).distinct(
        'device_user_token'
    )

    # Only send notifications if there are active iOS devices
    if ios_devices.exists():
        for device in ios_devices:
            notifications = []
            data = {
                'token': device.device_user_token,
                'alert': notification.body,
                'target': 'massnotification'
            }
            notifications.append(data)

            apple.send_push_notifications_multiple(notifications)

    # Mark the notification as delivered
    notification.state = MassNotification.STATE.DELIVERED
    notification.delivery_date = timezone.now()
    notification.save()
