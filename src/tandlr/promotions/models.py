# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models


class PromotionCode(models.Model):
    """
    Mapping table promotion_code in Tandlr.
    """
    expiration_date = models.DateTimeField(
        null=False,
        blank=False
    )

    code = models.CharField(
        max_length=31,
        blank=True,
        null=True,
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    discount = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=Decimal('0.00')
    )

    uses_per_user = models.IntegerField(
        default=1,
        help_text=u'Defines the number of times a user can use the promo code.'
    )

    class Meta:
        db_table = 'promotion_code'

    def __unicode__(self):
        return u'{0}'.format(self.code)

    @property
    def discount_percentage(self):
        return '%s %%' % self.discount


class BatchPromotionCode(models.Model):

    number = models.IntegerField()

    expiration_date = models.DateTimeField(
        null=False,
        blank=False,
        help_text=u'Time should be at least 15 minutes in the future.'
    )

    discount = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=Decimal('0.00')
    )

    def __unicode__(self):
        return u'{0}'.format(self.number)

    @property
    def discount_percentage(self):
        return '%s %%' % self.discount
