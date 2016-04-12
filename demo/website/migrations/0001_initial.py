# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-11 21:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ostinato_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseStudyPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_keywords', models.CharField(blank=True, max_length=250, null=True)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('content', models.TextField()),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_casestudypage_content', to='ostinato_pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContactPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_keywords', models.CharField(blank=True, max_length=250, null=True)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('content', models.TextField()),
                ('recipients', models.TextField(help_text=b'A comma separated list of recipient emails')),
                ('email_subject', models.CharField(max_length=250)),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_contactpage_content', to='ostinato_pages.Page')),
                ('success_page', mptt.fields.TreeForeignKey(help_text=b'The page to show the user once the form was succesfully submitted', on_delete=django.db.models.deletion.CASCADE, to='ostinato_pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GenericPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_keywords', models.CharField(blank=True, max_length=250, null=True)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('content', models.TextField()),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_genericpage_content', to='ostinato_pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_keywords', models.CharField(blank=True, max_length=250, null=True)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('content', models.TextField()),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_homepage_content', to='ostinato_pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TopLevelListPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_keywords', models.CharField(blank=True, max_length=250, null=True)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_toplevellistpage_content', to='ostinato_pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]