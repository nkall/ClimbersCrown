# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0003_athletecityscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='effortCount',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
