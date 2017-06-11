# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tandlr.users.models import User


class Balance(models.Model):

    teacher = models.ForeignKey(
        User,
        related_name='balances',
        verbose_name=_('teacher')
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created date')
    )
