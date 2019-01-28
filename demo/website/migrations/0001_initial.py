# Generated by Django 2.1.5 on 2019-01-18 15:19

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import website.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ostinato_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseStudyPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_keywords', models.CharField(blank=True, max_length=250, null=True)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('cache_page', models.BooleanField(default=False)),
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
                ('cache_page', models.BooleanField(default=False)),
                ('content', models.TextField()),
                ('recipients', models.TextField(help_text='A comma separated list of recipient emails')),
                ('email_subject', models.CharField(max_length=250)),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_contactpage_content', to='ostinato_pages.Page')),
                ('success_page', mptt.fields.TreeForeignKey(help_text='The page to show the user once the form was succesfully submitted', null=True, on_delete=django.db.models.deletion.SET_NULL, to='ostinato_pages.Page')),
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
                ('cache_page', models.BooleanField(default=False)),
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
                ('cache_page', models.BooleanField(default=False)),
                ('content', models.TextField()),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_homepage_content', to='ostinato_pages.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=(website.models.PageMediaMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('caption', models.CharField(blank=True, max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_visible', models.BooleanField(default=False)),
                ('image', models.ImageField(upload_to='uploads/')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TopLevelListPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_keywords', models.CharField(blank=True, max_length=250, null=True)),
                ('meta_description', models.TextField(blank=True, null=True)),
                ('cache_page', models.BooleanField(default=False)),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='website_toplevellistpage_content', to='ostinato_pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('caption', models.CharField(blank=True, max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_visible', models.BooleanField(default=False)),
                ('video_url', models.URLField()),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
    ]
