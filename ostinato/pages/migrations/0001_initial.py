# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-11 21:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('slug', models.SlugField(help_text='A url friendly slug.', unique=True, verbose_name='Slug')),
                ('short_title', models.CharField(blank=True, help_text='A shorter title which can be used in menus etc. If this is not supplied then the normal title field will be used.', max_length=50, null=True, verbose_name='Short title')),
                ('template', models.CharField(max_length=250, verbose_name='Template')),
                ('redirect', models.CharField(blank=True, help_text='Use this to point to redirect to another page or website.', max_length=200, null=True, verbose_name='Redirect')),
                ('show_in_nav', models.BooleanField(default=True, verbose_name='Show in nav')),
                ('show_in_sitemap', models.BooleanField(default=True, verbose_name='Show in sitemap')),
                ('state', models.IntegerField(choices=[(1, b'Private'), (5, b'Public')], default=5, verbose_name='State')),
                ('created_date', models.DateTimeField(blank=True, null=True, verbose_name='Created date')),
                ('modified_date', models.DateTimeField(blank=True, null=True, verbose_name='Modified date')),
                ('publish_date', models.DateTimeField(blank=True, null=True, verbose_name='Published date')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page_children', to='ostinato_pages.Page', verbose_name='Parent')),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
                'permissions': (('private_view_page', '[Private] Can View Page'), ('private_edit_page', '[Private] Can Edit Page'), ('private_delete_page', '[Private] Can Delete Page'), ('can_make_public_page', 'Can Make_public Page'), ('public_view_page', '[Public] Can View Page'), ('public_edit_page', '[Public] Can Edit Page'), ('public_delete_page', '[Public] Can Delete Page'), ('can_make_private_page', 'Can Make_private Page')),
            },
        ),
    ]
