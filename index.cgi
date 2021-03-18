#!/home/firenium/.linuxbrew/bin/python3.9
# -*- coding: utf-8 -*-
print("Content-type: text/plan\n")
print("<html><body>Python is awesome !</body></html>")

import sys, os
sys.path.insert(0, "/home/firenium/firenium.com/public_html/data/datavault")
import site
# Path to your python site-packages.
site.addsitedir('/home/firenium/.linuxbrew/bin/python3.9/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "datavault.settings.production"

from wsgiref.handlers import CGIHandler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
CGIHandler().run(application)