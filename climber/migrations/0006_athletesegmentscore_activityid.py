# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0005_athlete_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='athletesegmentscore',
            name='activityId',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
