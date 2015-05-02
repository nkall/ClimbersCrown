# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='id',
            field=models.AutoField(primary_key=True, verbose_name='ID', default=0, auto_created=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
