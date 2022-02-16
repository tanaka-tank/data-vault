#!/home/firenium/.linuxbrew/bin/python3.9
# -*- coding: utf-8 -*-
##print("Content-type: text/plan\n")
##print("<html><body>Python is awesome !</body></html>")

import sys, os
sys.path.insert(0, "/home/firenium/firenium.com/public_html/data/datavault/")
#
# Path to your python site-packages.
import site
site.addsitedir('/home/firenium/.linuxbrew/bin/python3.9/site-packages/bin')
#sys.path.insert(0, "/home/firenium/.linuxbrew/bin/python3.9/site-packages")

os.environ['DJANGO_SETTINGS_MODULE'] = "datavault.settings.production"

# numpy のスレッド（OpenBLAS)をsingle threadに制限する？？
os.environ["OPENBLAS_NUM_THREADS"] = "1"

from wsgiref.handlers import CGIHandler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
CGIHandler().run(application)