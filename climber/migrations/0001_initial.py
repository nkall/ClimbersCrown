# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='AthleteCityScore',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('cumulativeTime', models.IntegerField()),
                ('cityScore', models.IntegerField()),
                ('leaderboardPlacement', models.IntegerField()),
                ('athleteId', models.ForeignKey(to='climber.Athlete')),
            ],
        ),
        migrations.CreateModel(
            name='AthleteSegmentScore',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('effortId', models.IntegerField()),
                ('segmentTime', models.IntegerField()),
                ('segmentScore', models.IntegerField()),
                ('athleteId', models.ForeignKey(to='climber.Athlete')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('name', models.CharField(serialize=False, max_length=200, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlacementChange',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('oldPlacement', models.IntegerField()),
                ('newPlacement', models.IntegerField()),
                ('changeDate', models.DateTimeField()),
                ('athleteId', models.ForeignKey(to='climber.Athlete')),
                ('city', models.ForeignKey(to='climber.City')),
            ],
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('city', models.ForeignKey(to='climber.City')),
            ],
        ),
        migrations.AddField(
            model_name='athletesegmentscore',
            name='segmentId',
            field=models.ForeignKey(to='climber.Segment'),
        ),
        migrations.AddField(
            model_name='athletecityscore',
            name='city',
            field=models.ForeignKey(to='climber.City'),
        ),
    ]
