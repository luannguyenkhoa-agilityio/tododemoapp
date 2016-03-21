from __future__ import absolute_import
from django.db import models
from django.conf import settings
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import SmartResize
from ..commons.cache import img_url_cache
import uuid
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def get_unique_file_path(_, filename):
    ext = filename.split('.')[1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(settings.FILE_UPLOAD_PREFIX_FOLDER_USER, filename)

class UserImage(models.Model):
    original = ProcessedImageField(upload_to=get_unique_file_path,
                                   format='JPEG',
                                   options={'quality': 100})
    medium = ImageSpecField(source=original,
                            processors=[SmartResize(100, 100)],
                            format='JPEG',
                            options={'quality': 100})
    small = ImageSpecField(source=original,
                           processors=[SmartResize(50, 50)],
                           format='JPEG',
                           options={'quality': 100})

    @img_url_cache(img_type='original')
    def get_original_url(self):
        try:
            return self.original.url
        except Exception:
            return ''

    @img_url_cache(img_type='original')
    def get_medium_url(self):
        try:
            return self.medium.url
        except Exception:
            return ''

    @img_url_cache(img_type='original')
    def get_small_url(self):
        try:
            return self.small.url
        except Exception:
            return ''


class UserProfile(models.Model):
    class Meta:
        ordering = ['first_name']

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='userprofile', blank=True, null=True)
    # image = models.OneToOneField(UserImage, blank=True, null=True, related_name='image')
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.user.email if self.user else ''

