# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0004_auto_20150502_0045'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='gender',
            field=models.CharField(max_length=1, default='M'),
            preserve_default=False,
        ),
    ]
