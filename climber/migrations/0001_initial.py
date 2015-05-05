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
                ('gender', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='AthleteCityScore',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('cityScore', models.IntegerField()),
                ('rank', models.IntegerField()),
                ('athleteId', models.ForeignKey(to='climber.Athlete')),
            ],
        ),
        migrations.CreateModel(
            name='AthleteSegmentScore',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('effortId', models.IntegerField()),
                ('activityId', models.IntegerField()),
                ('segmentTime', models.IntegerField()),
                ('segmentScore', models.IntegerField()),
                ('athleteId', models.ForeignKey(to='climber.Athlete')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PlacementChange',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('oldRank', models.IntegerField()),
                ('newRank', models.IntegerField()),
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
        migrations.AlterUniqueTogether(
            name='athletesegmentscore',
            unique_together=set([('athleteId', 'segmentId')]),
        ),
    ]
