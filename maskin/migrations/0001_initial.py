# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.CharField(max_length=30, verbose_name='Phone number', blank=True)),
                ('program', models.CharField(blank=True, max_length=5, verbose_name='Program', choices=[(b'M', 'Mechanical engingering'), (b'DPU', 'Design and Product Development'), (b'EMM', 'Energy-Environment-Management'), (b'Master', 'Masterprogram'), (b'Other', 'Other')])),
                ('year', models.IntegerField(default=0, verbose_name='Year', validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)])),
                ('master', models.CharField(max_length=30, verbose_name='Master profile', blank=True)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='SchoolYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name='name')),
                ('start', models.DateField(unique=True, verbose_name='start')),
                ('end', models.DateField(unique=True, verbose_name='end')),
                ('member_group', models.OneToOneField(null=True, verbose_name='Member group', to='auth.Group')),
            ],
            options={
                'verbose_name': 'School year',
                'verbose_name_plural': 'School years',
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='member',
            field=models.ManyToManyField(to='maskin.SchoolYear', blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
