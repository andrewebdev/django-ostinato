# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-20 21:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='state',
            field=models.CharField(choices=[(b'review', b'Review'), (b'archived', b'Archived'), (b'private', b'Private'), (b'published', b'Published')], default=b'private', max_length=20, verbose_name='State'),
        ),
    ]
