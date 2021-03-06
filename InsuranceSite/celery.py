from __future__ import absolute_import 
import os
from celery import Celery
from django.conf import settings
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InsuranceSite.settings') 
 
youlinapp = Celery('InsuranceSite')
youlinapp.config_from_object('django.conf:settings')
youlinapp.autodiscover_tasks(lambda: settings.INSTALLED_APPS) 