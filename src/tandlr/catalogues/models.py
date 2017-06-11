# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tandlr.core.db.models.models import TimeStampedMixin


class University(TimeStampedMixin):
    """
    Catalogue of University.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('name'),
        unique=True
    )
    initial = models.CharField(
        max_length=50,
        verbose_name=_('initial')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active')
    )

    class Meta:
        verbose_name = _('university')
        verbose_name_plural = _('universities')

    def __unicode__(self):
        return self.name
