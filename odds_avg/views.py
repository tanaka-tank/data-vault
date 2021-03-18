from django.shortcuts import render
from django.http import HttpResponse
from django.utils import html
from django.template.defaultfilters import urlize

from django.views.generic import View
import urllib.request
import urllib.error
import datetime
from datetime import datetime as dt
import requests
import time
import json

#from .utils import *
from .utils import common
from .utils import boatrace
from .logic import boatraceoddsview
from .forms import XrentanForm

class BoatIndexView(View):
    # コンストラクタの定義
    #def __init__(self):
        #self.brovl = boatraceoddsview.BoatRaceOddsViewLogic()

    def get(self, req, *args, **kwargs):
        day = dt.today().strftime("%Y%m%d")
        params = {}
        #params['race_list'] = boatrace.BoatRaceUtils.get_race_info_3place(day)
        self.brovl = boatraceoddsview.BoatRaceOddsViewLogic()
        
        params['race_list'] = self.brovl.get_race_info_all_place(day)
        return render(req, 'odds_avg/index.html',params)

class XrentanView(View):

    # コンストラクタの定義
    def __init__(self):
        self.place = ''
        self.params = {'title_name':''}
        self.template_name = 'odds_avg/xrentan.html'
        self.brovl = boatraceoddsview.BoatRaceOddsViewLogic()

    """
        オッズ計算コントローラーget.
        Args:
            :params req: アクセス情報
        Returns:
            :params: Description of return render html
    """
    def get(self, req, *args, **kwargs):
        self.place = self.kwargs['place_name']
        bet_type = common.CommonUtils.get_query_string_bet_type(req.META['QUERY_STRING'],'bet_type')
        #get_last_time = dt.today().strftime('%Y-%m-%d %H:%M')
        #init_params = common.CommonUtils.power_merge_dict_d2(self.params, boatrace.BoatRaceUtils.get_init_params(bet_type,self.place,get_last_time))
        #print(bet_type)
        init_params = self.brovl.get_init_params(self.place,bet_type)
        init_params['submit_token']  = common.CommonUtils.set_submit_token(req)
        
        return render(req, self.template_name, init_params)
    
    """
        オッズ計算コントローラーpost.
        Args:
            :params req: アクセス情報
        Returns:
            :params: Description of return render html
    """
    def post(self, req, *args, **kwargs):
        self.place = self.kwargs['place_name']
        self.params['title_name'] = boatrace.BoatRaceUtils.get_place_name(self.place)

        #if common.CommonUtils.exists_submit_token(req) == False:
        #    return render(req, self.template_name, self.params)
        #self.params['submit_token'] = common.CommonUtils.set_submit_token(req)
        #self.params['f5_token'] = req.POST.get('submit_token')
        self.params['toushigaku'] = req.POST['toushigaku']
        self.params['race_deadline_time'] = req.POST['race_deadline_time']
        self.params['race_no'] = req.POST['race_no']
        self.params['order_zyun'] = req.POST['order_zyun']
        self.params['order_type'] = req.POST['order_type']
        
        META_QUERY_STRING = req.META['QUERY_STRING']
        bet_type = common.CommonUtils.get_query_string_bet_type(META_QUERY_STRING,'bet_type')
        upd = common.CommonUtils.get_query_string(META_QUERY_STRING,'upd')

        form = XrentanForm(req.POST)
        if not form.is_valid():
            req_data = json.loads(req.POST['post_data_json'])
            orth_target_odds_list = []
            for target_odds_row in req_data['target_odds_list']:
                orth_target_odds_list.append(json.loads(target_odds_row))
            order_param = {
                'order_zyun':self.params['order_zyun'],
                'order_type':self.params['order_type']
                }
            self.params['odds_list'] = self.brovl.get_new_odds_data(self.place,self.params['race_no'],orth_target_odds_list,bet_type,order_param)
            self.params['form'] = form
            return render(req, self.template_name,self.params)


        init_params = common.CommonUtils.power_merge_dict_d2(self.params, self.brovl.get_post_data_params(req, self.place, bet_type, upd))

        #init_params = common.CommonUtils.power_merge_dict_d2(self.params, boatrace.BoatRaceUtils.get_post_data_params(req, self.place, bet_type, upd))

        return render(req, self.template_name,init_params)