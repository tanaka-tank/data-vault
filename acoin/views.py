from django.shortcuts import render
from django.conf import settings
from django.views.generic import View
from .utils import *
from . import amazoncoinlogic
from django.conf.urls.static import static

class AcoinIndexView(View):
    global acl
    acl = amazoncoinlogic.AmazonCoinLogic()
        
    def index(req, *args, **kwargs):
        param = {}
        try:
            param_year = ''
            if "year" in req.GET and req.GET.get("year").isdecimal():
                param_year = req.GET.get("year")
            param = acl.get_amazon_coin_data_rows_data(param_year)
            ##if not Utils.is_access_valid(req):
            ##    return render(req, 'error/403.html')
            if Utils.is_ua_mobile_check(req):
                return render(req, 'acoin/sp/index.html',param)
            if not Utils.is_access_ua(req):
                return render(req, 'error/403.html')
        except FileNotFoundError as e:
            print("error: {0}".format(e))
            param['error'] = "error: FileNotFoundError"
        except ValueError as e:
            print("error: {0}".format(e))
            param['error'] = "error: ValueError"
        return render(req, 'acoin/index.html',param)
            

    def indexsp(req, *args, **kwargs):
        param_year = ''
        if "year" in req.GET:
            param_year = req.GET.get("year")
        param = acl.get_amazon_coin_data_rows_data(param_year)
    
        if not Utils.is_ua_mobile_check(req):
            return render(req, 'acoin/index.html',param)
        if not Utils.is_access_ua(req):
            return render(req, 'error/403.html')
        
        return render(req, 'acoin/sp/index.html',param)
    
    def chart1(req, *args, **kwargs):
        param_year = ''
        if "year" in req.GET:
            param_year = req.GET.get("year")
        param = acl.get_amazon_coin_data_chart1_data(param_year)
        param['yearly_list'] = acl.get_amazon_coin_data_yearly_list()
        if Utils.is_ua_mobile_check(req):
                return render(req, 'acoin/sp/chart1.html',param)
        if not Utils.is_access_ua(req):
            return render(req, 'error/403.html')
            
        return render(req, 'acoin/chart1.html',param)
