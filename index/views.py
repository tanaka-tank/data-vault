from django.shortcuts import render
from django.http import HttpResponse
from django.utils import html
from django.template.defaultfilters import urlize
from django.views.generic import View
from django.core.exceptions import PermissionDenied
import datetime
import random
import xml.etree.ElementTree as ET
import os
from django.conf import settings
# Create your views here.

class IndexView(View):
    def index(req, *args, **kwargs):
        params = {}
        params["random"] = IndexView.__noise()
        return render(req, 'index.html',params)
    
    def index403(req, *args, **kwargs):
        #if not self.request.user.is_authenticated:
        raise PermissionDenied

    def sitemap(req, *args, **kwargs):
        params = {}
        params["random"] = IndexView.__noise()
        IndexView.__create_sitemap()
        return render(req, 'index.html',params)
    
    def sitemapxml(req, *args, **kwargs):
        return HttpResponse(open(settings.STATIC_ROOT+'/xml/sitemap.xml').read(), content_type='text/xml')

    
    def __noise():
        return str(1 if random.random() >= 0.5 else 2)

    def __create_sitemap():
        urls = [
            "https://data.firenium.com/acoin/",
            "https://data.firenium.com/acoin/chart1/",
            "https://data.firenium.com/conv/",
            "https://data.firenium.com/conv/lcconvert/",
            "https://data.firenium.com/conv/clconvert/",
            "https://data.firenium.com/odds_avg/",
            "https://data.firenium.com/odds_avg/ashiya/",
            "https://data.firenium.com/odds_avg/omura/",
            "https://data.firenium.com/odds_avg/tokuyama/",
            "https://data.firenium.com/fontimage/",
            "https://data.firenium.com/fontimage/create/",
        ]
        
        urlset = ET.Element('urlset')
        urlset.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        urlset.set("xsi:schemaLocation", "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/siteindex.xsd")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        tree = ET.ElementTree(element=urlset)
        
        for url in urls:
            url_element = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url_element, 'loc')
            loc.text = url
            lastmod = ET.SubElement(url_element, 'lastmod')
            lastmod.text = datetime.date.today().strftime('%Y-%m-%d')
        return tree.write(settings.STATIC_ROOT+'/xml/sitemap.xml', encoding="utf-8", xml_declaration=True)