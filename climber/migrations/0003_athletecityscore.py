# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0002_auto_20150505_0048'),
    ]

    operations = [
        migrations.CreateModel(
            name='AthleteCityScore',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('cityScore', models.IntegerField()),
                ('rank', models.IntegerField()),
                ('athleteId', models.ForeignKey(to='climber.Athlete')),
                ('city', models.ForeignKey(to='climber.City')),
            ],
        ),
    ]
