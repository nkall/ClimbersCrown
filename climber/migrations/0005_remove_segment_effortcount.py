# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0004_segment_effortcount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='segment',
            name='effortCount',
        ),
    ]
