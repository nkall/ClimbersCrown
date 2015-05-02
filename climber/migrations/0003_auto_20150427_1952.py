# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0002_auto_20150426_0104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='id',
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
    ]
