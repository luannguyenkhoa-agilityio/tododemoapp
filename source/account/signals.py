from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from tastypie.models import create_api_key
from .models import UserImage, UserProfile
from ..commons.utils import delete_obsolete_img

models.signals.post_save.connect(create_api_key, sender=User)


@receiver(models.signals.post_save, sender=UserImage)
def pre_generator_image_s3_url(sender, **kwargs):
    try:
        img = kwargs["instance"]
        _ = img.original.url
        _ = img.medium.url
        _ = img.small.url
    except ValueError as e:
        print('pre_generator_image_s3_url %s' % e)
        pass


@receiver(models.signals.post_delete, sender=UserImage)
def delete_userimage_file(sender, **kwargs):
    try:
        img_obj = kwargs["instance"]
        delete_obsolete_img(img_obj)
    except ValueError as e:
        print('delete_userimage_file %s' % e)
        pass


@receiver(models.signals.post_delete, sender=UserProfile)
def delete_userprofile(sender, **kwargs):
    try:
        userprofile = kwargs["instance"]
        User.objects.filter(id=userprofile.user.id).delete()
    except ValueError as e:
        print('delete_userprofile %s' % e)
        pass
