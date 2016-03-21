# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, default='', null=True)),
                ('description', models.CharField(blank=True, max_length=255, default='', null=True)),
                ('select_date', models.CharField(blank=True, max_length=255, default='', null=True)),
                ('select_time', models.CharField(blank=True, max_length=255, default='', null=True)),
                ('all_day', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('location', models.CharField(blank=True, max_length=255, default='', null=True)),
                ('notification', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('repeat', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('task_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('user', models.ForeignKey(related_name='task', blank=True, to='account.UserProfile', null=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
