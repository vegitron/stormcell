# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stormcell', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='googleoauth',
            name='account_id',
            field=models.CharField(default=-1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='googleoauth',
            name='credential_id',
            field=models.CharField(default=-1, max_length=250),
            preserve_default=False,
        ),
    ]
