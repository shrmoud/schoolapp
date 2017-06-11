# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_save

from . import signals


class NotificationsAppConfig(AppConfig):
    """
    AppConfig for the ```tandlr.notifications``` module.
    """
    name = 'tandlr.notifications'
    verbose_name = 'Notifications'

    def ready(self):
        """
        Registers the signals that will be handled by this module.
        """
        post_save.connect(
            signals.send_push_notification_on_creation,
            sender=self.get_model('Notification')
        )
        post_save.connect(
            signals.schedule_push_notification_delivery,
            sender=self.get_model('MassNotification')
        )
