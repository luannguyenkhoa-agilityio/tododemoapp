from django.db import models
from ..account.models import UserProfile
from ..commons.datetime_utils import *
from django.utils import timezone
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class Task(models.Model):
    class Meta:
        ordering = ['title']

    user = models.ForeignKey(UserProfile, related_name='task', null=True, blank=True)

    title = models.CharField(max_length=255, default='', null=True, blank=True)
    description = models.CharField(max_length=255, default='', null=True, blank=True)
    select_date = models.CharField(max_length=255, default='', null=True, blank=True)
    select_time = models.CharField(max_length=255, default='', null=True, blank=True)
    all_day = models.PositiveIntegerField(default=0, null=True, blank=True)
    location = models.CharField(max_length=255, default='', null=True, blank=True)
    notification = models.PositiveIntegerField(default=0, null=True, blank=True)
    repeat = models.PositiveIntegerField(default=0, null=True, blank=True)

    is_deleted = models.BooleanField(default=False, blank=True)
    task_date = models.DateField(auto_now=False, default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.title
