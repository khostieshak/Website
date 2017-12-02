# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-11-19 15:23
from __future__ import unicode_literals

import advent_calendar.models
import aldryn_apphooks_config.fields
import app_data.fields
import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdventCalendarConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100, verbose_name='Type')),
                ('namespace', models.CharField(default=None, max_length=100, unique=True, verbose_name='Instance namespace')),
                ('app_data', app_data.fields.AppDataField(default=b'{}', editable=False)),
                ('start_date', models.DateField(verbose_name='start date')),
                ('publish_time', models.TimeField(verbose_name='publish time')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Apphook config',
                'verbose_name_plural': 'Apphook configs',
            },
        ),
        migrations.CreateModel(
            name='AdventCalenderDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField(verbose_name='start date')),
                ('app_config', aldryn_apphooks_config.fields.AppHookConfigField(default=None, help_text='When selecting a value, the form is reloaded to get the updated default', on_delete=django.db.models.deletion.CASCADE, to='advent_calendar.AdventCalendarConfig', verbose_name='calendar')),
                ('placeholder', cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, slotname=advent_calendar.models.placeholder_name, to='cms.Placeholder')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='adventcalendarconfig',
            unique_together=set([('type', 'namespace')]),
        ),
    ]