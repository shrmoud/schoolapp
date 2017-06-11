# -*- coding: utf-8 -*-
from django.db import models

from tandlr.users.models import User


class TypeCard(models.Model):
    """
    Mapping table type_card in Tandlr.
    """
    name = models.CharField(
        max_length=45,
        blank=False,
        null=False,
        unique=True
    )

    description = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'type_card'
        verbose_name_plural = u'card types'
        verbose_name = u'card type'


class Currency(models.Model):
    """
    Mapping table currency in Tandlr.
    """
    symbol = models.CharField(
        max_length=2,
        blank=False,
        null=False,
        unique=True
    )

    code = models.CharField(
        max_length=3,
        blank=False,
        null=False,
        unique=True
    )

    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return u'{0} - {1}'.format(self.symbol, self.code)

    class Meta:
        db_table = 'currency'
        verbose_name_plural = 'currencies'


class StatusPayment(models.Model):
    """
    Mapping table status_payment in Tandlr.
    """
    name = models.CharField(
        max_length=45,
        blank=False,
        null=False,
        unique=True
    )

    description = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'status_payment'
        verbose_name_plural = 'payment status'
        verbose_name = 'payment status'


class TypePayment(models.Model):
    """
    Mapping table type_payment in Tandlr.
    """
    name = models.CharField(
        max_length=45,
        blank=False,
        null=False,
        unique=True
    )

    description = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'type_payment'
        verbose_name = u'payment type'
        verbose_name_plural = u'payment types'


class PaymentMethod(models.Model):
    """
    Mapping table payment_method for payments in Tandlr.
    """
    name = models.CharField(
        max_length=45,
        blank=False,
        null=False,
        unique=True
    )

    description = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'payment_method'


class Card(models.Model):
    """
    Mapping table card in Tandlr.
    """
    token = models.TextField(
        blank=False,
        null=False,
        unique=True
    )

    numbers_card = models.IntegerField(
        null=False
    )

    user = models.ForeignKey(
        User,
        null=False,
        related_name='card'
    )

    type_card = models.ForeignKey(
        TypeCard,
        null=False
    )

    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return u'{0} - {1}'.format(
            self.type_card.name,
            self.user.get_full_name()
        )

    class Meta:
        db_table = 'card'


class AccountNumber(models.Model):
    """
    Mapping table account_number in Tandlr.
    """
    account_number = models.CharField(
        max_length=16,
        null=False,
        unique=True
    )

    user = models.ForeignKey(
        User,
        null=False,
        related_name='account'
    )

    type_card = models.ForeignKey(
        TypeCard,
        null=False
    )
    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return u'{0} - {1}'.format(
            self.account_number,
            self.user.get_full_name()
        )

    class Meta:
        db_table = 'account_number'


class TeacherPaymentInformation(models.Model):
    """
    Table designed to manage the information of the techer for the payment
    """

    teacher = models.OneToOneField(
        User,
        verbose_name='teacher'
    )
    bank = models.CharField(
        max_length=255,
        verbose_name='bank'
    )
    account_number = models.CharField(
        max_length=255,
        verbose_name='account number'
    )
    social_security_number = models.CharField(
        max_length=255,
        verbose_name='social security number'
    )

    class Meta:
        verbose_name_plural = "Teacher Payment Information"


class PayerPayment(models.Model):
    """
    Mapping table payer_payment in Tandlr.
    """
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=False
    )

    user = models.ForeignKey(
        User,
        null=False,
        related_name='payer'
    )

    payment_date = models.DateField(
        null=True
    )

    status_payment = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return u'{0} - {1}'.format(
            self.user.get_full_name(),
            self.amount
        )

    class Meta:
        db_table = 'payer_payment'


class Payment(models.Model):
    """
    Mapping payment in tandlr.
    """
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=False
    )

    user = models.ForeignKey(
        User,
        null=False,
        related_name='payment'
    )
    payment_date = models.DateField(
        null=True
    )

    type_payment = models.ForeignKey(
        TypePayment,
        null=False,
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        null=False,
    )
    card = models.ForeignKey(
        Card,
        null=True,
    )
    account_number = models.ForeignKey(
        AccountNumber,
        null=True,
    )
    currency = models.ForeignKey(
        Currency,
        null=False,
    )
    status_payment = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return u'{0} - {1}'.format(
            self.user.get_full_name(),
            self.amount
        )

    class Meta:
        db_table = 'payment'
