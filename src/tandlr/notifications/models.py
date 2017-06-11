# -*- coding: utf-8 -*-

from datetime import timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from tandlr.core.db.models import TimeStampedMixin


class Notification(TimeStampedMixin):
    """
    Model to store users' notifications.
    """
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        verbose_name=_('receiver'),
        help_text=_(
            'The user who has to receive the notification.'
        )
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='sent_notifications',
        verbose_name=_('sender'),
        help_text=_(
            'The user who sends the notification. Can be null if the '
            'notifications is originated by a system action.'
        )
    )

    target_type = models.ForeignKey(
        ContentType,
        blank=True, null=True,
        related_name='notifications',
        verbose_name=_('target type'),
        help_text=_(
            'The ContentType of the object that the notification points to.'
        )
    )
    target_id = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_('target id'),
        help_text=_(
            'The id of the object that the notification points to.'
        )
    )
    target_action = models.CharField(
        max_length=20,
        verbose_name=_('target action'),
        help_text=_(
            'The action triggered by the object that the notification '
            'points to.'
        )
    )
    target = GenericForeignKey('target_type', 'target_id')

    body = models.CharField(
        max_length=255,
        verbose_name=_('body'),
        help_text=_(
            'The message that will be displayed in the notificiation.'
        )
    )

    was_delivered = models.BooleanField(
        default=False,
        verbose_name=_('was delivered'),
        help_text=_(
            'Tells whether this notification was delivered to the receiver '
            'via push notificationsi or not.'
        )
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('is read'),
        help_text=_(
            'Tells whether this notification is already read by the '
            'receiver or not.'
        )
    )

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')

    @property
    def notifications_sent_in_last_period(self):
        return Notification.objects.filter(
            created_date__gte=(timezone.now() - timedelta(days=30))
        ).count()


class MassNotification(TimeStampedMixin):
    """
    Model to store notifications sent massively to a group of users.
    """
    class STATE:
        SCHEDULED = 100
        DELIVERED = 200

    STATE_CHOICES = (
        (STATE.SCHEDULED, _('scheduled').title()),
        (STATE.DELIVERED, _('delivered').title())
    )

    body = models.CharField(
        max_length=255,
        verbose_name=_('body'),
        help_text=_(
            'The message that will be displayed in the notificiation.'
        )
    )
    delivery_date = models.DateTimeField(
        verbose_name=_('delivery date'),
        help_text=_(
            'The date & time on which the notification will be sent.\n'
            'Note that setting a past date will cause the notification to '
            'be sent immediatelly.'
        )
    )
    university = models.ForeignKey(
        'catalogues.University',
        null=True, blank=True,
        related_name='notifications',
        verbose_name=_('university'),
        help_text=_(
            'The university whose users will be notified. Leave blank to '
            'notify all users of the platform.'
        )
    )
    state = models.IntegerField(
        default=STATE.SCHEDULED,
        choices=STATE_CHOICES,
        verbose_name=_('state'),
        help_text=_(
            'Tells whether the notification was already sent or it is '
            'scheduled for sending in future.'
        )
    )
    celery_task_id = models.CharField(
        max_length=36,
        verbose_name=_('celery task id'),
        help_text=_(
            'The id of the celery task that will actually send '
            'the notifications.'
        )
    )

    class Meta:
        verbose_name = _('mass notification')
        verbose_name_plural = _('mass notifications')

    def __unicode__(self):
        return self.body
