"""
Django settings for tododemo project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from __future__ import absolute_import
from os.path import abspath, basename, dirname, join, normpath
from sys import path
from os import environ
from .base import *
import logging, copy
from django.utils.log import DEFAULT_LOGGING

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'todoappdb',
        'USER': 'app_user',
        'PASSWORD': 'app_passwd',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
######### END DATABASE CONFIGURATION

########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
######### END CACHE CONFIGURATION

########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'debug.middlewares.QueryCountDebugMiddleware',
    # 'common.middlewares.ProfileMiddleware',
    # 'common.middlewares.SQLLogToConsoleMiddleware'
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION

########## IMAGE URL CONFIGURATION
IMAGE_URL_PROTOCOL = 'http:'
IMAGE_CUSTOM_DOMAIN = 'localhost:8000/media'
########## END IMAGE URL CONFIGURATION


########## LOGGING CONFIGURATION
LOGGING = {
    'version':1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'file_error.log'
        },
        'tododemo': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'tododemo.log'
        },
        'distribute': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'distribute.log'
        },
        'rq_scheduler': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'rq_scheduler_error.log'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': 'True'
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True
        },
        'debug.middleware': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
        'tododemo': {
            'handlers': ['tododemo'],
            'level': 'ERROR'
        },
        'distribute': {
            'handlers': ['distribute'],
            'level': 'ERROR'
        },
        'rq_scheduler': {
            'handlers': ['rq_scheduler'],
            'level': 'ERROR'
        }
    }
}

########## TASTYPIE CONFIGURATION
TASTYPIE_FULL_DEBUG = True

########## END TASTYPIE CONFIGURATION

########## UPLOAD FILE CONFIGURATION

FILE_UPLOAD_PREFIX_FOLDER_USER = 'user'

########## UPLOAD FILE CONFIGURATION

########## FIX DJANGO19 WARNING

LOGGING = copy.deepcopy(DEFAULT_LOGGING)
LOGGING['filters']['suppress_deprecated'] = {
    '()': 'tododemo.settings.local.SuppressDeprecated'  
}
LOGGING['handlers']['console']['filters'].append('suppress_deprecated')

class SuppressDeprecated(logging.Filter):
    def filter(self, record):
        WARNINGS_TO_SUPPRESS = [
            'RemovedInDjango18Warning',
            'RemovedInDjango19Warning'
        ]
        # Return false to suppress message.
        return not any([warn in record.getMessage() for warn in WARNINGS_TO_SUPPRESS])
######### END         