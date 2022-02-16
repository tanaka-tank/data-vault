from django.shortcuts import render
from django.http import HttpResponse
from django.utils import html
from django.template.defaultfilters import urlize
from django.views.generic import View
import urllib.request, urllib.error
from .forms import ConvForm
# Create your views here.

class ConvIndexView(View):
    def index(req, *args, **kwargs):
        return render(req, 'conv/index.html')
    
    def conv_lcconvert(req, *args, **kwargs):
        """
            改行→カンマ変換コントローラー.
            Args:
                list.dist req :アクセス情報
            Returns:
                :param: Description of return render html
        """
        convert_list = {}
        params = {}
        if req.method == 'GET':
            return render(req, 'conv/conv_lc.html')
        elif req.method == 'POST':
            before_text = req.POST["convert_before_name"]
            if not before_text:
                return render(req, 'conv/conv_lc.html')
            
            params['before_text'] = before_text
            form = ConvForm(req.POST)
            if not form.is_valid():
                params['form'] = form
                return render(req, 'conv/conv_lc.html',params)
            
            if "add_type" in req.POST:
                convert_list['_quote'] = req.POST["add_type"]
            else:
                convert_list['_quote'] = 'default'
            ConvIndexView.__to_quote_data(convert_list)
            
            after_text = convert_list['_pause'].join(before_text.split())
            after_text = convert_list['_pre_suf'] + after_text+convert_list['_pre_suf']
            
            params['after_text'] = after_text
            params[convert_list['_quote']] = convert_list['_quote']
            return render(req, 'conv/conv_lc.html',params)
    
    def conv_clconvert(req, *args, **kwargs):
        """
            カンマ→改行変換コントローラー.
            Args:
                list.dist req :アクセス情報
            Returns:
                :param: Description of return render html
        """
        params = {}
        if req.method == 'GET':
            return render(req, 'conv/conv_cl.html')
        elif req.method == 'POST':
            before_text = req.POST["convert_before_name"]
            if not before_text:
                return render(req, 'conv/conv_cl.html')
            
            params['before_text'] = before_text
            form = ConvForm(req.POST)
            if not form.is_valid():
                params['form'] = form
                return render(req, 'conv/conv_cl.html',params)
            
            after_text = before_text.replace(',', '\n')

            params['before_text'] = before_text
            params['after_text'] = after_text
            return render(req, 'conv/conv_cl.html',params)
    
    ##def conv_colonconvert(req, *args, **kwargs):
    ##    """
    ##        コロン→改行変換コントローラー.
    ##        Args:
    ##        :param req: アクセス情報
    ##        :type req: list.dist
    ##        Returns:
    ##        :param: Description of return render html
    ##    """
    ##    params = {}
    ##    if req.method == 'GET':
    ##        return render(req, 'conv/conv_colon.html')
    ##    elif req.method == 'POST':
    ##        before_text = req.POST["convert_before_name"]
    ##        if not before_text:
    ##            return render(req, 'conv/conv_colon.html')
    ##        trans_table = str.maketrans(':：', '\n\n', '')
    ##        after_text = before_text.translate(trans_table)
    ##        # after_text = before_text.replace(':', '\n')
    ##        params['before_text'] = before_text
    ##        params['after_text'] = after_text
    ##        return render(req, 'conv/conv_colon.html',params)
    
    #クオーテーション条件
    def __to_quote_data(convert_list):
        """クオーテーション条件関数.
        Args:
            convert_list dict :クオーテーション条件
        Returns:
            dict: トリムデータ
        """
        if convert_list['_quote'] == 'single_quote':
            convert_list['_pause'] = '\',\''
            convert_list['_pre_suf'] = '\''
            convert_list['single_quote'] = '1'
        elif convert_list['_quote'] == 'double_quote':
            convert_list['_pause'] = '","'
            convert_list['_pre_suf'] = '"'
            convert_list['double_quote'] = '1'
        else:
            convert_list['_pause'] = ','
            convert_list['_pre_suf'] = ''
            convert_list['no_quote'] = '1'
