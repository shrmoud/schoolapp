# -*- coding: utf-8 -*-
from django.contrib.gis.geos import GEOSGeometry

from tandlr.utils import make_thumbnail

from .decorators import skip_signal


@skip_signal()
def make_thumbnail_user(sender, instance, created, *args, **kwargs):
    """
    Generates a thumbnail (size:400x400) image to show
    instead of the original one.
    """
    # The image must exist to create a thumb of it.

    if instance.photo:
        make_thumbnail(
            instance, 'photo', 'thumbnail', '400x400'
        )

    # create attribute skip_signal to prevent recrusion, then save then delete
    # attribute

    instance.skip_signal = True

    instance.save()

    del instance.skip_signal


def crate_settings(sender, instance, created, *args, **kwargs):
    """
    Signal for create settings for the user
    """
    from .models import UserSettings, LocationUser, UserSummary
    if created:
        UserSettings.objects.create(user=instance)
        UserSummary.objects.create(user=instance)

        point = GEOSGeometry('SRID=4326;POINT({0} {1})'.format(0, 0))
        LocationUser.objects.create(user=instance, point=point)
