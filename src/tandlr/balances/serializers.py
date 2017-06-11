# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from rest_framework import serializers

from tandlr.balances.models import Balance
from tandlr.scheduled_classes.models import ClassBill
from tandlr.users.serializers import UserShortV2Serializer


class BalanceV2Serializer(serializers.ModelSerializer):

    teacher = UserShortV2Serializer()
    current_total = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Balance
        fields = (
            'id',
            'teacher',
            'current_total',
            'total'
        )

    def get_total(self, instance):

        balance = Balance.objects.filter(
            teacher=instance.teacher,
        ).aggregate(
            total=Sum(F('bills__subtotal'))
        )

        return balance.get('total', Decimal('0.00'))

    def get_current_total(self, instance):

        #
        # We devide the month in two sections.
        # From the 1st to the 15th and from the 15th to the end of month. If
        # the current date is less than the 15th, then we need to take all
        # the bills from the 1st to the current date, otherwise we need to
        # take all the bills from the 15th to the current date.
        #

        date_range = []
        today = timezone.localtime(timezone.now())
        tomorrow = today + timedelta(days=1)
        if today.day < 15:
            date_range = [
                datetime(
                    year=today.year,
                    month=today.month,
                    day=1,
                    tzinfo=today.tzinfo
                ),
                datetime(
                    year=tomorrow.year,
                    month=tomorrow.month,
                    day=tomorrow.day,
                    tzinfo=today.tzinfo
                )
            ]
        else:
            date_range = [
                datetime(
                    year=today.year,
                    month=today.month,
                    day=15,
                    tzinfo=today.tzinfo
                ),
                datetime(
                    year=tomorrow.year,
                    month=tomorrow.month,
                    day=tomorrow.day,
                    tzinfo=today.tzinfo
                )
            ]

        balance = Balance.objects.filter(
            teacher=instance.teacher,
            bills__created_at__range=date_range
        ).aggregate(
            total=Sum(F('bills__subtotal'))
        )

        return balance.get('total', Decimal('0.00'))


class BalanceBillsV2Serializer(serializers.ModelSerializer):

    class Meta:
        model = ClassBill
        fields = (
            'id',
            'subtotal',
            'created_at'
        )
