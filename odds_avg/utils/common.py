import os
import uuid
import math
import numpy as np
import importlib
from django.http import QueryDict
from django.conf import settings

class CommonUtils:
    
    def is_access_valid(req):
        if 'csrftoken' in req.COOKIES:
            return True
        return False
    
    def is_access_ua(req):
        """uaのあるアクセスか判定する
        Args:
            req list.dist :アクセス情報
        Returns:
            boolean: 判定結果
        """
        if 'HTTP_USER_AGENT' in req.META and ('google' in req.META['HTTP_USER_AGENT'].upper() or 'google' in req.META['HTTP_USER_AGENT'].lower()):
            return True
        if 'HTTP_USER_AGENT' in req.META and 'HTTP_ACCEPT_LANGUAGE' in req.META:
            return True
        else:
            return False
    
    def is_ua_mobile_check(req):
        """モバイルアクセスか確認する
        Args:
            req list.dist :アクセス情報
        Returns:
            boolean: 判定結果
        """
        ua_string = req.META["HTTP_USER_AGENT"] #本番はこっち
        ##user_agent = parse(ua_string)
        ##print(ua_string)
        if CommonUtils.__is_mobile(ua_string):
            return True
        else:
            return False
    
    @staticmethod
    def get_const_path():
        """settingsファイルの環境変数を見てコンスタントファイルのパスを取得する
        Returns:
            string: 環境によるコンスタントファイルのパス
        """
        return os.path.join('odds_avg.conf.const')
    
    def get_query_string(meta_query_string,query_key):
        """クエリストリングの値を取得する
        Args:
            meta_query_string string :HttpRequest.method クエリストリング全文字列
            query_key string :クエリストリングのキー値
        Returns:
            list: クエリストリングの値
        """
        dct = QueryDict(meta_query_string)
        dct_list = dct.getlist(query_key)
        if len(dct_list) == 0:
            return ''
        return dct_list[0]
        
    def get_query_string_bet_type(meta_query_string,query_key):
        """クエリストリングの値を取得する
        Args:
            meta_query_string string :HttpRequest.method クエリストリング全文字列
            query_key string :クエリストリングのキー値
        Returns:
            list: クエリストリングの値
        """
        const_path = importlib.import_module(CommonUtils().get_const_path())
        bet_type_list = CommonUtils.get_query_string(meta_query_string,query_key)
        if bet_type_list == const_path.BET_2TAN:
            return bet_type_list
        if bet_type_list == const_path.BET_2PUKU:
            return bet_type_list
        if bet_type_list == const_path.BET_3PUKU:
            return bet_type_list
        return const_path.BET_3TAN
    
    def set_submit_token(req):
        submit_token = str(uuid.uuid4())
        
        f5_submit_token = ''
        if not req.POST.get('submit_token') is None:
            f5_submit_token = req.POST.get('submit_token')
        
        if not 'submit_token' in req.session.keys():
            req.session['submit_token'] = submit_token
        if not 'f5_submit_token' in req.session.keys():
            req.session['f5_submit_token'] = f5_submit_token

        return submit_token
    
    def exists_submit_token(req):
        token_in_request = req.POST.get('submit_token')
        token_in_session = req.session.pop('submit_token', '')
        token_in_f5      = req.session.pop('f5_submit_token', '')
        #print('token_in_request ;'+token_in_request)
        #print('token_in_session ;'+token_in_session)
        #print('token_in_f5      ;'+token_in_f5)
    
        if not token_in_request:
            return False
        if not token_in_session:
            return False

        if token_in_f5 == token_in_request:
            return True
    
        return token_in_request == token_in_session

    def power_merge_dict_d1(d1, d2):
        """辞書結合ひとつめの辞書を優先する
        Args:
            d1 dict :優先辞書型
            d2 dict :結合辞書型
        Returns:
            dict: 結合値
        """
        d_merged = d1.copy()
        for k, v in d2.items():
            if not k in d_merged:
                d_merged[k] = v
        return d_merged

    def power_merge_dict_d2(d1, d2):
        """辞書結合ふたつめの辞書で上書きする
        Args:
            d1 dict :結合辞書型
            d2 dict :優先辞書型
        Returns:
            dict: 結合値
        """
        d_merged = d1.copy()
        d_merged.update(d2)
        return d_merged

    def is_race_period(self,race_time_list: list,target_time:str) -> bool:
        """
        開催期間判定
        Args:
            race_time_list list : 開催期間の文字列
            target_time str     : 比較したい時
        Returns:
            boolean : 開催期間判定結果
        """
        start_time = self.time_minus_or_plus_one_ymdhm(race_time_list[0],-30,0)
        end_time   = self.time_minus_or_plus_one_ymdhm(race_time_list[11],7,0)

        if start_time <= target_time and target_time <= end_time:
            return True
        return False

    def time_minus_or_plus_one_ymdhm(self,time_str: str,add_time = 0,add_second = 0) -> str:
        """
        時間を元に1時間マイナスした値にし日付＋時間で返す
        Args:
            time_str str   : hh:mm形式の文字列時間
            add_time str   : 操作したい時
            add_second str : 操作したい分
        Returns:
            str:yyyymmdd hh:mm形式のマイナスされた時間
        """
        import datetime
        from datetime import datetime as dt

        now_ymd = dt.today().strftime("%Y%m%d")
        #時間型に変換する
        #print(type(time_str))
        #print("id(time_str) = %s" % id(time_str))
        conv_time = dt.strptime(now_ymd+' '+time_str, '%Y%m%d %H:%M')
        #print(conv_time)
        return str(conv_time + datetime.timedelta(minutes=add_time,seconds=add_second))
    
    def get_sorted_odds_list(__xrentna_list,sort_param):
        """
        Args:
            __xrentna_list list:レース順list
            sort_param dict:ソート情報
        Returns:
            list: 3行目昇順でソートした2次元配列
        """
        reverse_flag = False
        if sort_param['order_zyun'] == 'asc':
            reverse_flag = False
        if sort_param['order_zyun'] == 'desc':
            reverse_flag = True

        order_type_keyfunc = CommonUtils.__keyfunc_col2
        if sort_param['order_type'] == 'sort_odds':
            order_type_keyfunc = CommonUtils.__keyfunc_col2
        if sort_param['order_type'] == 'sort_funaban':
            order_type_keyfunc = CommonUtils.__keyfunc_col1
        #print(sort_param)
        return sorted(__xrentna_list, reverse=reverse_flag, key=order_type_keyfunc)#key=lambda x: x[2])
    
    def __keyfunc_col2(x):
        """sorted用のkey 2列目でソートしfloatを数値順にstrは無限にする
        Args:
            x list[]:ソート対象の2次元配列
        Returns:
            float:ソート用に変換したfloat値
        """
        if CommonUtils.is_float(x[2]) and x[2] != '0.0':
            return float(x[2])
        elif CommonUtils.is_float(x[2]) and x[2] == '0.0':
            return float('inf')
        else:
            return float('inf')

    def __keyfunc_col1(x):
        """sorted用のkey 1列目でソートしfloatを数値順にstrは無限にする
        Args:
            x list[]:ソート対象の2次元配列
        Returns:
            float:ソート用に変換したfloat値
        """
        if CommonUtils.is_float(x[1]) and x[1] != '0.0':
            return float(x[1])
        elif CommonUtils.is_float(x[1]) and x[1] == '0.0':
            return float('inf')
        else:
            return float('inf')
    
    def round_tens_value(calc_val):
        """10の位で切り上げ切り下げを判定する
        Args:
            calc_val float :判定対象データ
        Returns:
            float: 処理結果
        """
        calc_val = CommonUtils.__org_round(calc_val)
        s = str(calc_val)
        #オッズが高すぎて合成オッズで割った時1桁の場合100を返す
        if len(s) < 2:
            return 100
        if s[-2] == '0' or s[-2] == '1' or s[-2] == '2'or s[-2] == '3'or s[-2] == '4':
            return math.floor(calc_val/100) * 100
        else:
            return math.ceil(calc_val/100) * 100

    def __org_round(a:np.ndarray) -> np.ndarray:
        """正しく丸めるround
        ((a%1)==0.5)*(a//1%2==0)がやっていることとしては(a%1)==0.5で*.5の形になっているところだけに1が立つarrayを作り, 
        a//1%2==0で整数部分が偶数になっているところだけに1が立つarrayを作ってそれらをかけることで, (偶数).5 になっているところにだけ1を足すような愚直な方法になっています。
        このやり方は(pythonでは遅いと言われる)for文を使わないので、forを使って愚直にやるより若干の速さの改善が見込まれます。
        """
        rounded_a = np.round(a)+(((a%1)==0.5)*(a//1%2==0))
        return int(rounded_a)

    def __is_mobile(ua_string):
        """uaを利用してモバイル判定
        Args:
            ua_string string :ua
        Returns:
            boolean: 判定結果
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

    def __is_duplicates2d(l_2d):
        """リストに重複した要素があるか判定（要素にリストがある場合）
        Args:
            l_2d list[] :2次元配列
        Returns:
            boolean: 判定結果
        """
        seen = []
        unique_list = [x for x in l_2d if x not in seen and not seen.append(x)]
        return len(l_2d) != len(unique_list)
    
    def is_float(str):
        """https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
        Args:
            str string :判定文字列
        Returns:
            boolean: 判定結果
        """
        try:
          float(str)
          return True
        except ValueError:
          return False