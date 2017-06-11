# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_classes', '0004_class_participants'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default='SRID=4326;POINT (19.4619810000000015 -99.1511504000000059)', srid=4326),
            preserve_default=False,
        ),
    ]
