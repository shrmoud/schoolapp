# -*- coding: utf-8 -*-
import random

from datetime import timedelta
from hashlib import sha1

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from tandlr.core.db.models import TimeStampedMixin
from tandlr.logs.models import LogMail
from tandlr.users.models import User


class ActivationKeysManager(models.Manager):

    def reset_user_password(self, email, request=None):
        """
        Custom reset password
        """
        user = User.objects.get(
            email=email
        )
        # Create activation_key
        salt = sha1(str(random.random())).hexdigest()[:5]
        key = sha1(salt + user.username).hexdigest()
        ResetPassword.objects.create(
            user=user, activation_key=key
        )
        url = '{}{}'.format('tandlr://', key)

        url_web = '{}{}/{}'.format(
                settings.FRONTEND_RECOVERY_PASSWORD_URL,
                key,
                user.email
        )
        # Constructs the context to be passed to the renderer.
        context = {
            'user': user,
            'site': url,
            'activation_link': url,
            'activation_key': key,
            'request': request,
            'activation_link_web': url_web
        }

        # Gets the email subject in a single line.
        message_subject = render_to_string(
            'email/passwords/reset_password_subject.txt',
            context
        )
        message_subject = ''.join(message_subject.splitlines())

        # Renders the plain text message.
        message_text = render_to_string(
            'email/passwords/reset_password.txt',
            context
        )

        # Renders the html message.
        message_html = render_to_string(
            'email/passwords/reset_password.html',
            context
        )

        # Send a mail with the data for account activation
        user.email_user(message_subject, message_text, message_html)

        LogMail(
            user=user,
            mail_from=user.email,
            mail_subject='Registration user',
        ).save()

        return user

    def activation_user(self, user, request=None):
        """
        Custom activation user
        """
        context = {
            'user': user,
            'frontend_login_url': settings.FRONTEND_BASE_HOST,
            'request': request,
            'request_url_scheme': request.META['wsgi.url_scheme']
        }

        # Gets the email subject in a single line.
        message_subject = render_to_string(
            'email/registration/confirmation_email_subject.txt',
            context
        )
        message_subject = ''.join(message_subject.splitlines())

        # Renders the plain text message.
        message_text = render_to_string(
            'email/registration/confirmation_email.txt',
            context
        )

        # Renders the html message.
        message_html = render_to_string(
            'email/registration/confirmation_email.html',
            context
        )

        # Send a mail with the data for account activation
        user.email_user(message_subject, message_text, message_html)

        return user


class RegistrationProfile(TimeStampedMixin):
    """
    Mapping table registration_profile in Tandlr.
    """
    user = models.OneToOneField(User)

    activation_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name=_('activation key')
    )
    is_activated = models.BooleanField(
        default=False,
        verbose_name=_('is activated')
    )

    objects = ActivationKeysManager()

    class Meta:
        verbose_name = _('Registration Profile')
        verbose_name_plural = _('Registration Profiles')

    @property
    def key_expired(self):
        """
        Tells wheter the activation key of the current profile is expired.
        The key is expired if the user was already activated or the current
        date is greater than the user's date that the user was joined plus
        the validity minutes of the key.
        Returns a boolean.
        """
        if not self.is_activated:
            return (True if (now() - self.created_date) >
                    timedelta(days=1) else False)

        return True


class ResetPassword(TimeStampedMixin):
    """
    Mapping table reset password for users.
    """
    user = models.ForeignKey(
        User,
        related_name='reset_password'
    )
    activation_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name=_('activation key')
    )
    is_activated = models.BooleanField(
        default=False,
        verbose_name=_('is activated')
    )

    objects = ActivationKeysManager()

    class Meta:
        verbose_name = _('Reset Password')
        verbose_name_plural = _('Reset Passwords')

    @property
    def key_expired(self):
        """
        Tells wheter the activation key of the current profile is expired.
        The key is expired if the user was already activated or the current
        date is greater than the user's date that the user was joined plus
        the validity minutes of the key.
        Returns a boolean.
        """
        if not self.is_activated:
            return (True if (now() - self.created_date) >
                    timedelta(minutes=15) else False)

        return True
