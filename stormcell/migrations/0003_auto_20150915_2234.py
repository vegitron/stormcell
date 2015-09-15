# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stormcell', '0002_auto_20150915_2228'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='googleoauth',
            unique_together=set([('user', 'account_id')]),
        ),
    ]
