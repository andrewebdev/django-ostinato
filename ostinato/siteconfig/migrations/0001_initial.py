# Generated by Django 2.1.5 on 2019-09-09 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('setting_key', models.CharField(max_length=200, unique=True)),
                ('value_type', models.CharField(choices=[('str', 'String'), ('int', 'Integer Number'), ('dec', 'Decimal Number'), ('bool', 'Boolean (yes/no)')], default='string', max_length=25)),
                ('setting_value', models.TextField(blank=True, null=True)),
            ],
        ),
    ]