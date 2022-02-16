#!/usr/bin/python3
# -*- coding: utf-8 -*-
print("Content-type: text/plan\n")
print("<html><body>Python is awesome !</body></html>")
import sys, os
sys.path.insert(0, "/home/firenium/firenium.com/public_html/data/datavault")
import site
# Path to your python site-packages.
site.addsitedir('/home/firenium/.linuxbrew/Cellar/python@3.9/3.9.1_9/lib/python3.9/site-packages')
#site.addsitedir('/home/firenium/.linuxbrew/bin/python3.9/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = "datavault.settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")