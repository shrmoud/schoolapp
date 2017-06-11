# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_save

from . import signals


class UsersAppConfig(AppConfig):
    """
    AppConfig for the ```tandlr.users``` module.
    """
    name = 'tandlr.users'
    # verbose_name = 'Users'
    # app_label=''

    def ready(self):
        """
        Registers the signals that will be handled by this module.
        """
        super(UsersAppConfig, self).ready()

        user_model = self.get_model('User')
        post_save.connect(
            signals.make_thumbnail_user,
            sender=user_model
        )
        post_save.connect(
            signals.crate_settings,
            sender=user_model
        )
