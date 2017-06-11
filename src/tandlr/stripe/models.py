# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from tandlr.scheduled_classes.models import Class


class StripeCard(models.Model):

    card_id = models.CharField(
        null=True, blank=True,
        max_length=255,
        verbose_name=_("stripe id")

    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("created at")
    )

    customer = models.ForeignKey(
        'StripeCustomer',
        verbose_name=_("customer")
    )

    name = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("name")
    )

    address_line_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("address line 1")
    )

    address_line_1_check = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("address line 1 check")
    )

    address_line_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("address line 2")
    )

    address_city = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("address city")
    )

    address_state = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("address state")
    )

    address_country = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("address country")
    )

    address_zip = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("address zip")
    )

    address_zip_check = models.CharField(
        max_length=15,
        null=True,
        verbose_name=_("address zip check")
    )

    brand = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("brand")
    )

    country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name=_("country")
    )

    cvc_check = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("cvc check")
    )

    dynamic_last4 = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_("dynamic last 4 digits")
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name=_("default card")
    )

    tokenization_method = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("tokenization method")
    )

    exp_month = models.IntegerField(
        verbose_name=_("expiration month")
    )

    exp_year = models.IntegerField(
        verbose_name=_("expiration year")
    )

    funding = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("funding")
    )

    last4 = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name=_("last 4 digits")
    )

    fingerprint = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("fingerprint")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active")
    )


class StripeCustomer(models.Model):
    """
    The customer object allows the platform to perform recurring charges and
    track multiple charges that are associated with the same customer.
    """

    customer_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("stripe id")
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("created at")
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        verbose_name=_("user")
    )

    account_balance = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        null=True,
        verbose_name=_("account balance")
    )

    currency = models.CharField(
        max_length=10,
        default="usd",
        verbose_name=_("currency")
    )

    delinquent = models.BooleanField(
        default=False,
        verbose_name=_("deliquent")
    )

    default_source = models.TextField(
        blank=True,
        verbose_name=_("default source")
    )

    date_purged = models.DateTimeField(
        null=True,
        editable=False,
        verbose_name=_("date purged")
    )

    def __unicode__(self):
        return self.customer_id


class StripeCharge(models.Model):
    """
    The charge is an special type of object created when a succesfull resquest
    was managed by Stripe.
    """

    charge_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("stripe id")
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("created at")
    )

    customer = models.ForeignKey(
        StripeCustomer,
        related_name="charges",
        verbose_name=_("customer")
    )

    card = models.ForeignKey(
        StripeCard,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="charges",
        verbose_name=_("card")
    )

    currency = models.CharField(
        max_length=10,
        default="usd",
        verbose_name=_("currency")
    )

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        null=True,
        verbose_name=_("amount")
    )

    amount_refunded = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        null=True,
        verbose_name=_("amount refunded")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description")
    )

    paid = models.NullBooleanField(
        null=True,
        verbose_name=_("paid")
    )

    disputed = models.NullBooleanField(
        null=True,
        verbose_name=_("disputed")
    )

    refunded = models.NullBooleanField(
        null=True,
        verbose_name=_("refunded")
    )

    captured = models.NullBooleanField(
        null=True,
        verbose_name=_("captured")
    )

    charge_created = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("charge created")
    )

    related_class = models.ForeignKey(
        Class,
        related_name="payments",
        verbose_name=_("related class")
    )
