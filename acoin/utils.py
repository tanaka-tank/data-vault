import os
import csv
import importlib
from django.conf import settings
from datetime import datetime

class Utils:
    def __init__(self, value):
        self.value = value
    
    def is_access_valid(req):
        if 'csrftoken' in req.COOKIES:
            return True
        return False
        
    def is_access_ua(req):
        """
        Args:
            req list.dist:アクセス情報
        Returns:
            boolean:判定結果
        """
        if 'HTTP_USER_AGENT' in req.META and ('google' in req.META['HTTP_USER_AGENT'].upper() or 'google' in req.META['HTTP_USER_AGENT'].lower()):
            return True
        if 'HTTP_USER_AGENT' in req.META and 'HTTP_ACCEPT_LANGUAGE' in req.META:
            return True
        else:
            return False
    
    def is_ua_mobile_check(req):
        """
        Args:
            req list.dist:アクセス情報
        Returns:
            boolean:判定結果
        """
        ua_string = req.META["HTTP_USER_AGENT"] #本番はこっち
        ##user_agent = parse(ua_string)
        ##print(ua_string)
        if Utils.__is_mobile(ua_string):
            return True
        else:
            return False
    
    def get_const_path():
        """settingsファイルの環境変数を見てコンスタントファイルのパスを取得する
        Returns:
            string:環境によるコンスタントファイルのパス
        """
        if settings.ENV == 'develop':
            return os.path.join('acoin.conf'+'.'+settings.ENV+'.const')
        return os.path.join('acoin.conf.const')
    
    def convert_ymd(row):
        """先頭行の日付をスラッシュ区切りに変換する
        Args:
            row list: 変換対象配列(行想定)
        Returns:
            list:変換後配列
        """
        row[0] = Utils.convert_slash(row[0])
        return row
    
    def convert_slash(tstr):
        """8桁の文字列をスラッシュ区切りに変換する
        Args:
            tstr string: 変換前文字列
        Returns:
            string:変換後文字列
        """
        nstr = tstr[:4] + '/' + tstr[4:6] + '/' + tstr[6:]
        return nstr
    
    def __is_mobile(ua_string):
        """
        Args:
            ua_string string: ua
        Returns:
            boolean:判定結果
        """
        if  'BlackBerry OS' in ua_string and 'Blackberry Playbook' not in ua_string:
            return True
        if 'J2ME' in ua_string or 'MIDP' in ua_string:
            return True
        # This is here mainly to detect Google's Mobile Spider
        if 'iPhone;' in ua_string:
            return True
        if 'Googlebot-Mobile' in ua_string:
            return True
        # Nokia mobile
        if 'NokiaBrowser' in ua_string and 'Mobile' in ua_string:
            return True
        if (('iPhone' in ua_string or 'Android' in ua_string) and 'Mobile' in ua_string):
            return True
        return False
