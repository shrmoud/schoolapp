# -*- coding: utf-8 -*-
import time

from apns import APNs, Frame, Payload

from celery import shared_task

from django.conf import settings

import pytz


def _get_apns_connection():
    """
    Returns an instance of ```apns.APNs``` ready to interact with the
    Apple Push Notification Service (APNs).
    """
    return APNs(
        use_sandbox=getattr(settings, 'APNS_USE_SANDBOX', True),
        cert_file=getattr(settings, 'APNS_CERT_FILE_PATH', ''),
        key_file=getattr(settings, 'APNS_KEY_FILE_PATH', None)
    )


@shared_task
def send_push_notification(token, alert, sound='default', badge=1, **kwargs):
    """
    Send a push notification to the Apple Push Notification service (APNs).

    Params:
        token (str): The device token where the notification will be delivered.
        alert (str): The message that shall be displayed to the user.
        sound (options[str]): The sound that shall be played on the user's
            device. Defaults to 'default'.
        badge (int): The badge number to be displayed on the app icon.
            Defaults to 1.
        **kwargs: Arbitrary custom arguments that shall be sent with
            the notification.

    Returns:
        None
    """
    apns = _get_apns_connection()
    payload = Payload(alert=alert, sound=sound, badge=badge, custom=kwargs)
    apns.gateway_server.send_notification(token, payload)


@shared_task
def send_push_notifications_multiple(notifications):
    """
    Sends multiple push notifications to the Apple Push Notification
    service (APNs) in a single connection.

    Params:
        notifications (list): A list containing dictionary objects with the
            parameters that should be passed to the APNs.

    Returns:
        int: the number of bytes sent to the APNs
    """
    frame = Frame()
    apns = _get_apns_connection()
    expiry = time.time() + (len(notifications) * 5)
    priority = 10

    for index, notification in enumerate(notifications, 1):
        frame.add_item(
            notification.pop('token'),
            Payload(
                alert=notification.pop('alert'),
                sound=notification.pop('sound', 'default'),
                badge=notification.pop('badge', 1),
                custom=notification
            ),
            index, expiry, priority
        )

    return apns.gateway_server.write(frame.get_frame())


@shared_task
def delete_failed_ios_devices():
    """
    Connects to the APNs feedback service to retrieve the list of devices that
    have failed to receive a notification and deletes them from the database
    to optimize the amount of messages sent with mass notifications.

    This task must be executed periodically.
    """
    from tandlr.users.models import DeviceUser

    apns = _get_apns_connection()

    for token, fail_time in apns.feedback_server.items():
        try:
            device = DeviceUser.objects.get(
                device_user_token=token,
                device_os='iOS'
            )

        except DeviceUser.DoesNotExist:
            continue

        # DIRTY HACK: The datetime returned from the apns is offset-naive, but
        # Apple states in the documentation that this time is in UTC, so we
        # add this timezone to the fail_time to be able to compare it with the
        # device's last_modified attribute.
        fail_time = fail_time.replace(tzinfo=pytz.UTC)

        if device.is_active and device.last_modified <= fail_time:
            device.delete()
