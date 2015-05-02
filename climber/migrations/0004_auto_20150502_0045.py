# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climber', '0003_auto_20150427_1952'),
    ]

    operations = [
        migrations.RenameField(
            model_name='athletecityscore',
            old_name='leaderboardPlacement',
            new_name='rank',
        ),
        migrations.RenameField(
            model_name='placementchange',
            old_name='newPlacement',
            new_name='newRank',
        ),
        migrations.RenameField(
            model_name='placementchange',
            old_name='oldPlacement',
            new_name='oldRank',
        ),
    ]
