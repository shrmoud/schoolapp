# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_teacherpaymentinformation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teacherpaymentinformation',
            options={'verbose_name_plural': 'Teacher Payment Information'},
        ),
    ]
