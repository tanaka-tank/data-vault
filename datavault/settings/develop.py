"""
Django settings for quantumgrail project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

from .base import *

INSTALLED_APPS += (
                   # 'debug_toolbar', # and other apps for local development
                   )
ALLOWED_HOSTS = ['*']
#STATIC_URL = '/static/'

#MEDIA_URL = '/temp_media/'
ENV = 'develop'
