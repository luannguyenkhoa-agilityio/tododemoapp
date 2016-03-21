from __future__ import absolute_import
from django.conf import settings

url_protocol = getattr(settings, 'IMAGE_URL_PROTOCOL', 'http:')
custom_domain = getattr(settings, 'IMAGE_CUSTOM_DOMAIN', None)

def img_url_cache(img_type=None, prefix='img'):

    def _real_decorator(func):
        def _wraps(*args, **kwargs):
            context = args[0]   
            if custom_domain:
                return "%s//%s/%s" % (url_protocol, custom_domain, getattr(context, img_type).name)
            return func(context)

        return _wraps

    return _real_decorator