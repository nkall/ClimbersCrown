# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0006_athletesegmentscore_activityid'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='athletesegmentscore',
            unique_together=set([('athleteId', 'segmentId')]),
        ),
    ]
