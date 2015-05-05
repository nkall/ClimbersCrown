# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='athletecityscore',
            name='athleteId',
        ),
        migrations.RemoveField(
            model_name='athletecityscore',
            name='city',
        ),
        migrations.DeleteModel(
            name='AthleteCityScore',
        ),
    ]
