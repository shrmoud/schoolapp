# -*- coding: utf-8 -*-
from decimal import Decimal as D  # noqa

from django import template

from django.conf import settings
from django.db.models import Sum

register = template.Library()


@register.simple_tag()
def calculate_extrension_class_price(booking):
    return calculate_price(booking)


@register.simple_tag()
def get_total_price_extension_class(booking):
    return booking.subject.price_per_hour + calculate_price(booking)


@register.simple_tag()
def get_total_time_extesion_class(booking):
    return calculate_time(booking) + 1


def calculate_time(booking):
    bookings = booking.extensions_time_class.aggregate(Sum('time'))
    if not bookings['time__sum']:
        return 0

    total_seconds = bookings['time__sum'].total_seconds()

    return total_seconds / 3600


def calculate_price(booking):
    if booking.extensions_time_class.count > 0:
        total_hours = calculate_time(booking)
        hours_price = D(total_hours) * booking.subject.price_per_hour

        return hours_price.quantize(D(settings.MONEY_QUANTIZE_FORMAT))

    else:
        return 0
