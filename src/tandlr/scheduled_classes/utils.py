# -*- coding: utf-8 -*-
from decimal import Decimal as D

from django.conf import settings


def calculate_price_per_extrension_class(price_per_hour, time):
    """
    Calculates the price per fraction of time.
    This is used when making the stripe charge for class extension.
    """
    minutes_price = time.minute / D('60') * price_per_hour
    hours_price = D(time.hour) * price_per_hour

    price = minutes_price + hours_price

    return price.quantize(D(settings.MONEY_QUANTIZE_FORMAT))
