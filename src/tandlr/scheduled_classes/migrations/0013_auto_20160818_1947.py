# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogues', '0001_initial'),
        ('scheduled_classes', '0012_auto_20160805_1954'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'verbose_name': 'session', 'verbose_name_plural': 'sessions'},
        ),
        migrations.AddField(
            model_name='subject',
            name='university',
            field=models.ForeignKey(related_name='subjects', default=14, to='catalogues.University'),
            preserve_default=False,
        ),
    ]
