import os
import csv

import json
import importlib
import datetime
from datetime import datetime as dt
from django.conf import settings
from bs4 import BeautifulSoup
import requests
import pandas as pd
import math
import numpy as np
import urllib
import time
import lxml.html
#import dask.dataframe as dd

from logging import getLogger
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from . import common
from . import boatraceraw
from ..logic import scrapingbatch

class BoatRaceUtils:
    ## 開催日当日yyyymmdd
    today = dt.today().strftime("%Y%m%d")
    ## 環境ディレクトリ
    global const_path
    const_path = importlib.import_module(common.CommonUtils().get_const_path())

    ## logger
    global logger
    logger = getLogger("file")
    
    def get_init_params(bet_type,place,get_last_time):
        """初期情報作成
        Args:
            req WSGIRequest list.dist: アクセス情報
            bet_type string :買い方
            place string :競艇場
        Returns:
            list: 初期値データ群
        """
        start = time.time()
        day = dt.today().strftime("%Y%m%d")
        if day != BoatRaceUtils.today:
            BoatRaceUtils.today = day
        try:
            today_full = dt.today().strftime('%Y%m%d%H%M%S%f')[:-3]
            race_no = BoatRaceUtils.get_race_no(place)
            #print(race_no)
            
            params = {
                'now_date':'',
                'race_no': '',
                'race_deadline_time': '',
                'get_last_time' : get_last_time
            }
            if race_no == '0':
                return common.CommonUtils.power_merge_dict_d2(params,{'result':'レース期間外','error':'no_element'})
                
            params['now_date'] = today_full
            params['race_no'] = race_no

            params['race_deadline_time'] = BoatRaceUtils.get_race_deadline_time(place,race_no)

            #_odds_data = BoatRaceUtils.get_odds_xrentan_data(place,bet_type)
            order_param={'order_zyun':'asc','order_type':'sort_odds'}
            _odds_data = boatraceraw.BoatRaceRawUtils.get_odds_xrentan_data_list_origin(place,bet_type,order_param)
            
            if 'error' in _odds_data[0]:
                params.update(_odds_data[0])
            else:#isinstance(_odds_data[0], list):
                params['odds_list'] = _odds_data
        except Exception as e:
            message = 'システムエラー[初期情報]'
            logger.error(message + '： {}'.format(e))
            return {'result':message,'error':e}
        finally:
            elapsed_time = time.time() - start
            print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        return params

    def get_post_data_params(req,place,bet_type,upd_flag=''):
        """更新情報作成
        Args:
            req WSGIRequest list.dist :入力データ
            place string :競艇場
            bet_type string :買い方
            upd_flag string:更新のみ処理フラグ
        Returns:
            dict: 入力結果計算データ
        """
        start = time.time()

        race_no = BoatRaceUtils.get_race_no(place)
        order_param={'order_zyun':'asc','order_type':'sort_odds'}

        if req.POST['race_no'] != race_no:
            params = {'result':'レース時間超過','error':'time_over'}
            
            params['odds_list'] = boatraceraw.BoatRaceRawUtils.get_odds_xrentan_data_list_origin(place,bet_type,order_param)
            return params
        
        result = {
            'toushigaku':req.POST["toushigaku"],
            'race_deadline_time': BoatRaceUtils.get_race_deadline_time(place,race_no),
            'get_last_time':dt.today().strftime('%Y-%m-%d %H:%M')
            }

        req_data_json = req.POST['post_data_json']
        req_data = json.loads(req_data_json)
        orth_target_odds_list = []
        for item in req_data['target_odds_list']:
            orth_target_odds_list.append(json.loads(item))

        order_param = BoatRaceUtils.__get_sort_column_num(req)
        
        try:
            if upd_flag != '1':
                #result['odds_list'] = boatrace.BoatRaceUtils.get_calc_odds_data(place,orth_target_odds_list,result['toushigaku'],bet_type)
                result['odds_list'] = boatraceraw.BoatRaceRawUtils.get_calc_odds_data(place,orth_target_odds_list,result['toushigaku'],bet_type,order_param)
            if upd_flag == '1':
                #result['odds_list'] = boatrace.BoatRaceUtils.get_new_odds_data(place,orth_target_odds_list,bet_type)
                result['odds_list'] = boatraceraw.BoatRaceRawUtils.get_new_odds_data(place,orth_target_odds_list,bet_type,order_param)
        except KeyError as e:
            message = 'レース期間外'
            logger.info(message + '： {}'.format(e))
            return result.update({'result':message,'error':e})
        finally:
            elapsed_time = time.time() - start
            print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        return result

    def get_place_name(place):
        """
        Args:
            place string:競艇場
        Returns:
            string: 競艇場名
        """
        if not BoatRaceUtils.is_effect_place(place):
            return '無登録競艇'
        if place == 'ashiya':
            return '芦屋競艇オッズ'
        if place == 'omura':
            return '大村競艇オッズ'
        if place == 'tokuyama':
            return '徳山競艇オッズ'

    def get_odds_xrentan_data(place,bet_type='3'):
        """scrapingされた3連単のオッズデータ取得
        Args:
            place string:競艇場
            bet_type string:買い方
        Returns:
            dict: csvファイルの辞書型データ
        """
        if not BoatRaceUtils.is_effect_place(place):
            return [{'result':'レース場対象外','error':'no_place'}]
        result = []

        #if bet_type == '3':
        #    result = BoatRaceUtils.__create_3rentan_odds_file(place)
        #if bet_type == '2':
        #    result = BoatRaceUtils.__create_2rentan_odds_file(place)

        #result = BoatRaceUtils.__create_xrentan_odds_file(place,bet_type)

        #print(BoatRaceUtils.__get_odds_race_order_list(place,'11',bet_type))

        #if result and isinstance(result[0], dict) and result[0]['error']:
        #    return result

        return BoatRaceUtils.__get_odds_marge_csv_data_list(place,bet_type)

    
    def get_calc_odds_data(place,target_odds_list,toushigaku,bet_type):
        """scrapingされたオッズデータ取得
        Args:
            place string:競艇場
            target_odds_list list:計算対象データリスト
            toushigaku string:投資金額
            bet_type string:買い方
        Returns:
            dict: csvファイルの辞書型データ
        """
        if not BoatRaceUtils.is_effect_place(place):
            return [{'result':'レース場対象外','error':'no_place'}]
        change_list = []
        change_list_append = change_list.append
        #target_odds_list = __mobius_equation(target_odds_list,toushigaku)
        target_odds_list = BoatRaceUtils.__get_compose_odds(target_odds_list,toushigaku)
    
        for base_row in BoatRaceUtils.get_odds_xrentan_data(place,bet_type):
            add_flag = 0
            for target_row in target_odds_list: 
                if str(target_row['odds_no']) == str(base_row[0]):
                    change_list_append(list(target_row.values()))
                    add_flag = 1
            if add_flag == 0:
                change_list_append(base_row)
        return change_list
    
    def get_new_odds_data(place,target_odds_list,bet_type):
        """scrapingされたオッズデータ取得
        Args:
            place string:競艇場
            target_odds_list list:計算対象データリスト
        Returns:
            dict: csvファイルの辞書型データ
        """
        if not BoatRaceUtils.is_effect_place(place):
            return [{'result':'レース場対象外','error':'no_place'}]
        change_list = []
        change_list_append = change_list.append
        
        for base_row in BoatRaceUtils.get_odds_xrentan_data(place,bet_type):
            add_flag = 0
            for target_row in target_odds_list: 
                if str(target_row['odds_no']) == str(base_row[0]):
                    #target_row['checked'] = 'checked'
                    base_row.append('checked')
                    change_list_append(base_row)
                    #change_list_append(list(target_row.values()))
                    add_flag = 1
            if add_flag == 0:
                change_list_append(base_row)
        return change_list

    def get_race_no(place):
        """
        Args:
            place string:競艇場
        Returns:
            string: レース順
        """
        if place == 'ashiya':
            return BoatRaceUtils.__get_ashiya_race_no()
        if place == 'omura':
            return BoatRaceUtils.__get_omura_race_no()
        if place == 'tokuyama':
            return BoatRaceUtils.__get_tokuyama_race_no()

    def get_race_no_all():
        """
        レース順全一覧取得
        Args:
            place string:競艇場
        Returns:
            list: レース順リスト
        """
        race_nos = {}
        ashiya_no = BoatRaceUtils.get_race_no_csv_relative('ashiya')['race_no']
        omura_no = BoatRaceUtils.get_race_no_csv_relative('omura')['race_no']
        tokuyama_no = BoatRaceUtils.get_race_no_csv_relative('tokuyama')['race_no']
        if ashiya_no != '0':
            race_nos['ashiya'] = ashiya_no
        if omura_no != '0':
            race_nos['omura'] = omura_no
        if tokuyama_no != '0':
            race_nos['tokuyama'] = tokuyama_no

        return race_nos

    def get_race_no_csv_relative(place):
        """ csvファイルから現在時刻で相対的にレース番号を取得する
        Args:
            day string:yyyymmdd
        Returns:
            list: レース開催情報まとめ
        """
        result = {
            'race_no': '0',
            'race_deadline_time': ''
            }
        csv_file = open(const_path.BOATRACE_DEADLINE_TIMES_CSV, 'r', encoding='utf_8', errors='', newline='')
        csv_data = csv.reader(csv_file, delimiter=',', doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        csv_data_list = list(csv_data)

        #csv_data = dd.read_csv(const_path.BOATRACE_DEADLINE_TIMES_CSV, header=None, encoding='utf_8').compute()
        #csv_data_list = csv_data.values.tolist()

        ccu = common.CommonUtils()
        now_time = dt.today().strftime('%Y-%m-%d %H:%M:%S')

        #step = 1
        for row in csv_data_list:
            if BoatRaceUtils.get_place_to_jcd(place) == str(row[0]):
                race_time_list = list(row[3].strip("][").replace("'", "").split(','))
                #開催期間判定
                if not ccu.is_race_period(race_time_list,now_time):
                    return result
                for i,deadline_row in enumerate(race_time_list):
                    i+=1
                    #レース時間が3分ほどなので3分後まで,最終は7分後まで表示させておく
                    add_time = 3
                    if i == 1:
                        add_time = -30
                    if i == 12:
                        add_time = 7
                    if now_time <= ccu.time_minus_or_plus_one_ymdhm(deadline_row,add_time,0):
                        result['race_no'] = str(i)
                        result['race_deadline_time'] = dt.strptime(dt.today().strftime("%Y%m%d")+' '+deadline_row, '%Y%m%d %H:%M')
                        return result
                    #step+=1
        return result

    def get_race_deadline_time(place,race_no):
        """ レース締切時間を取得する
        Args:
            place string:競艇場
            race_no string:レース順
        Returns:
            string: レース締切時間
        """
        if not BoatRaceUtils.is_effect_place(place):
            return ''
        
        jcd = ""
        if place == 'ashiya':
            jcd = '21'
        if place == 'omura':
            jcd = '24'
        if place == 'tokuyama':
            jcd = '18'

        load_url = "https://www.boatrace.jp/owpc/pc/race/raceindex?jcd=" + jcd + "&hd=" + BoatRaceUtils.today
        
        html = urllib.request.urlopen(load_url)

        soup = BeautifulSoup(html, "html.parser",from_encoding="utf-8")
        if soup.find_all("div",attrs={"class": "table1"}):
            table_element = soup.find("div",attrs={"class": "table1"}).find_all_next('tbody')
            for i, table in enumerate(table_element, 1):
                if str(i) == race_no:
                    return table.find("tr").find_all("td")[1].text
    
    def get_race_no_and_race_deadline_time(place):
        """ レース締切時間と番号をまとめて取得
        Args:
            place string:競艇場
        Returns:
            string: レース締切時間
        """
        if not BoatRaceUtils.is_effect_place(place):
            return ''

        result = {'race_no':'0','fixed_time':'対象時間外'}
        jcd = ""
        if place == 'ashiya':
            jcd = '21'
        if place == 'omura':
            jcd = '24'
        if place == 'tokuyama':
            jcd = '18'

        load_url = "https://www.boatrace.jp/owpc/pc/race/raceindex?jcd=" + jcd + "&hd=" + BoatRaceUtils.today
        
        html = urllib.request.urlopen(load_url)
        soup = BeautifulSoup(html, "html.parser",from_encoding="utf-8")
        if soup.find_all("div",attrs={"class": "table1"}):
            element_soup = soup.find("div",attrs={"class": "table1"})
            table_element = element_soup.find_all_next('tbody')

            for i, table in enumerate(table_element, 1):
                if table.find("tr").find_all("td")[2].text != '' and table.find("tr").find_all("td")[2].text != '発売終了':
                    result['race_no'] = table.find("tr").find_all("td")[0].contents[1].text
                    result['fixed_time'] = table.find("tr").find_all("td")[1].text
                    break
        return result

    def get_race_info_3place(day):
        """ 開催レースをまとめて取得
        Args:
            day string:yyyymmdd
        Returns:
            list: レース開催情報まとめ
        """
        result = [{'get_day':BoatRaceUtils.today}]
        result_append = result.append

        if day != BoatRaceUtils.today:
            #print(day+' ; '+BoatRaceUtils.today)
            BoatRaceUtils.today = day
            #print(day+' ; '+BoatRaceUtils.today)
            result = [{'get_day':day}]
        
        jcds = ['21','24','18']
        urls= []
        for jcd in jcds:
            urls.append("https://www.boatrace.jp/owpc/pc/race/raceindex?jcd=" + jcd + "&hd=" + BoatRaceUtils.today)
        
        mapfunc = partial(requests.get, headers={'Referer' :'https://www.google.com/','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'})
        with ThreadPoolExecutor(4) as executor:
            url_response_results = list(executor.map(mapfunc, urls))

        for i,url_response_one in enumerate(url_response_results):
            stb = {'jcd':'','target_day':BoatRaceUtils.today,'place_name':'','title_name':''}

            soup = BeautifulSoup(url_response_one.content, "html.parser",from_encoding="utf-8")
            lxml_coverted_data = lxml.html.fromstring(str(soup))
            
            if len(lxml_coverted_data.xpath('/html/body/main/div/div/div/div[1]/h2/span')) != 0:
                continue
            stb['jcd'] = jcds[i]
            stb['place_name'] = lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[1]/div/div[1]/img/@alt)')
            stb['title_name'] = lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[1]/div/div[2]/h2)')
            stb['start_time'] = lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[1]/tr/td[2])')
            stb['end_time'] = lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[12]/tr/td[2])')
            
            result_append(stb)
        #print(result)
        return result
    
    def is_effect_place(place):
        """scrapingされたオッズデータ取得
        Args:
            place string:競艇場
        Returns:
            boolean: 判定結果
        """
        if place == 'ashiya' or place == 'omura' or place == 'tokuyama' or place =='all':
            return True
        return False

    def get_jcd_cd_all():
        """ レース場に対するjcd一覧の取得
        Returns:
            list: jcdコードのリスト
        """
        return ['12','17','18','19','21','24']

    def get_place_to_jcd(place):
        """ レース場に対するjcdの取得
        Args:
            place string:競艇場
        Returns:
            string: jcd
        """
        if place == 'ashiya':
            return '21'
        if place == 'omura':
            return '24'
        if place == 'tokuyama':
            return '18'
        if place == 'suminoe':
            return '12'

    def get_odds_file_full_path(bet_type,place,race_no):
        """ レース場に対するjcdの取得
        Args:
            bet_type string:ベットタイプ
            place string:競艇場
            race_no string:レース番号
        Returns:
            string: file_full_path
        """
        return const_path.BOATRACE_STORAGE_DIR + place + '/' + 'odds_' + bet_type + '_' +  race_no + 'r.csv'
    
    def get_odds_file_update_time(csv_path):
        """ オッズファイルの更新時間取得
        Args:
            csv_path string:CSVフルパス
        Returns:
            string: yyyyy/mm/dd hh:mm
        """
        ddft = datetime.datetime.fromtimestamp(os.stat(csv_path).st_mtime)
        return ddft.strftime('%Y/%m/%d %H:%M')
    
    def get_sort_column_num(req):
        """
        Args:
            req list:入力情報
        Returns:
            dict: ソート順
        """
        params = {'order_zyun': req.POST['order_zyun'],'order_type': req.POST['order_type']}
        return params
    
    def __get_odds_csv(place,bet_type='3'):
        """odds_csvファイルを取得する
        Args:
            place string:競艇場
            bet_type string:買い方
        Returns:
            string: csvのフルパス
        """
        
        if place == 'ashiya' and bet_type == '2':
            return const_path.ODDS_ASHIYA_2RENTAN_CSV
        if place == 'ashiya' and bet_type == '3':
            return const_path.ODDS_ASHIYA_3RENTAN_CSV
        if place == 'omura' and bet_type == '2':
            return const_path.ODDS_OMURA_2RENTAN_CSV
        if place == 'omura' and bet_type == '3':
            return const_path.ODDS_OMURA_3RENTAN_CSV
        if place == 'tokuyama' and bet_type == '2':
            return const_path.ODDS_TOKUYAMA_2RENTAN_CSV
        if place == 'tokuyama' and bet_type == '3':
            return const_path.ODDS_TOKUYAMA_3RENTAN_CSV
    
    def __get_odds_race_order_csv(bet_type='3'):
        """odds_race_order_csvファイルを取得する
        Args:
            bet_type string:買い方
        Returns:
            string: csvのフルパス
        """
        if bet_type == '2':
            return const_path.ODDS_RACE_ORDER_2RENTAN_CSV
        if bet_type == '3':
            return const_path.ODDS_RACE_ORDER_3RENTAN_CSV
        return const_path.ODDS_RACE_ORDER_3RENTAN_CSV
    
    def __get_marge_odds_csv(place,bet_type='3'):
        """marge_odds_csvファイルを取得する
        Args:
            place string:競艇場
            bet_type string:買い方
        Returns:
            string: csvのフルパス
        """
        if place == 'ashiya' and bet_type == '2':
            return const_path.MARGE_ODDS_ASHIYA_2RENTAN_CSV
        if place == 'ashiya' and bet_type == '3':
            return const_path.MARGE_ODDS_ASHIYA_3RENTAN_CSV
        if place == 'omura' and bet_type == '2':
            return const_path.MARGE_ODDS_OMURA_2RENTAN_CSV
        if place == 'omura' and bet_type == '3':
            return const_path.MARGE_ODDS_OMURA_3RENTAN_CSV
        if place == 'tokuyama' and bet_type == '2':
            return const_path.MARGE_ODDS_TOKUYAMA_2RENTAN_CSV
        if place == 'tokuyama' and bet_type == '3':
            return const_path.MARGE_ODDS_TOKUYAMA_3RENTAN_CSV
    
    def __get_odds_marge_csv_data_list(place,bet_type='3'):
        """オッズファイルのオッズの昇順でソートする
        Args:
            place string:競艇場
            bet_type string:買い方
        Returns:
            csv.reader object list: csv情報の配列
        """
        csv_file_name = BoatRaceUtils.__get_marge_odds_csv(place,bet_type)
        
        csv_file = open(csv_file_name, 'r', encoding='utf_8', errors='', newline='')
        csv_data = csv.reader(csv_file, delimiter=',', doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        csv_data_list = list(csv_data)

        #csv_data = dd.read_csv(csv_file_name).compute()
        #csv_data_list = csv_data.values.tolist()

        #csv_file = open(csv_file_name, "r", encoding="utf-8", errors="", newline="" )
        #file_list = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        #rows = [[row[0], row[1].replace("'", '')] for row in file_list]
    
        # 2列目でソートして返却
        return sorted(BoatRaceUtils.__conv_str_to_number(csv_data_list), key=BoatRaceUtils.__keyfunc)
        
    def __keyfunc(x):
        """sorted用のkey 2列目でソートしfloatを数値順にstrは無限にする
        Args:
            x list[]:ソート対象の2次元配列
        Returns:
            float:ソート用に変換したfloat値
        """
        if type(x[2]) == float and x[2] != 0.0:
            return x[2]
        elif type(x[2]) == float and x[2] == 0.0:
            return float('inf')
        else:
            return float('inf')
    
    def __conv_str_to_number(rows):
        """csvで読み込んだ値を数値型の部分を変換する
        Args:
            rows list[]:csvから読み込んだ2次元配列
        Returns:
            list[]:順番とオッズを数値に変換した2次元配列
        """
        conv_list = []
        conv_list_append = conv_list.append

        num = 1
        for out_row in rows:
            try:
                conv_list_append([num,int(out_row[0]),float(out_row[1])])
            except ValueError as instance:
                conv_list_append([num,int(out_row[0]),out_row[1]])
            num += 1
        return conv_list

    def create_xrentan_odds_file(place,bet_type,req_race_no=''):
        """scrapingされた2,3連単csvファイルのデータ作成
        Args:
            place string:競艇場
            bet_type string:買い方
        Returns:
            dict: 処理結果
        """
        if not req_race_no:
            race_no = req_race_no
        else:
            race_no = BoatRaceUtils.get_race_no(place)
            if race_no == '0':
                return [{'result':'レース期間外','error':'no_element'}]
        
        sbl = scrapingbatch.ScrapingBatchLogic()
        result = []
        if place == 'ashiya' and bet_type == const_path.BET_3TAN:
            result = sbl.create_ashiya_3rentan_odds_file(place,race_no,bet_type)
        if place == 'ashiya' and bet_type == const_path.BET_3PUKU:
            result = sbl.create_ashiya_3renpuku_odds_file(place,race_no,bet_type)
        if place == 'ashiya' and bet_type == const_path.BET_2TAN:
            result = sbl.create_ashiya_2ren_odds_file(place,race_no,bet_type)
        if place == 'ashiya' and bet_type == const_path.BET_2PUKU:
            result = sbl.create_ashiya_2ren_odds_file(place,race_no,bet_type)
        if place == 'omura' and bet_type == const_path.BET_3TAN:
            result = sbl.create_omura_3rentan_odds_file(place,race_no,bet_type)
        if place == 'omura' and bet_type == const_path.BET_3PUKU:
            result = sbl.create_omura_3renpuku_odds_file(place,race_no,bet_type)
        if place == 'omura' and bet_type == const_path.BET_2TAN:
            result = sbl.create_omura_2ren_odds_file(place,race_no,bet_type)
        if place == 'omura' and bet_type == const_path.BET_2PUKU:
            result = sbl.create_omura_2ren_odds_file(place,race_no,bet_type)
        if place == 'tokuyama' and bet_type == const_path.BET_3TAN:
            result = sbl.create_tokuyama_3rentan_odds_file(place,race_no,bet_type)
        if place == 'tokuyama' and bet_type == const_path.BET_3PUKU:
            result = sbl.create_tokuyama_3renpuku_odds_file(place,race_no,bet_type)
        if place == 'tokuyama' and bet_type == const_path.BET_2TAN:
            result = sbl.create_tokuyama_2ren_odds_file(place,race_no,bet_type)
        if place == 'tokuyama' and bet_type == const_path.BET_2PUKU:
            result = sbl.create_tokuyama_2ren_odds_file(place,race_no,bet_type)
        
        if not result or not result['error']:
            BoatRaceUtils.__marge_odds_file(place)
    
        return [{'result':'正常終了','error':''}]

    def __create_3rentan_odds_file(place):
        """scrapingされた3連単csvファイルのデータ作成
        Args:
            place string:競艇場
        Returns:
            dict: 処理結果
        """
        race_no = BoatRaceUtils.get_race_no(place)

        if race_no == '0':
            return [{'result':'レース期間外','error':'no_element'}]
    
        result = []
        if place == 'ashiya':
            result = BoatRaceUtils.__create_ashiya_3rentan_odds_file(place,race_no)
        if place == 'omura':
            result = BoatRaceUtils.__create_omura_3rentan_odds_file(place,race_no)
        if place == 'tokuyama':
            result = BoatRaceUtils.__create_tokuyama_3rentan_odds_file(place,race_no)
        
        if not result or not result['error']:
            BoatRaceUtils.__marge_odds_file(place)
    
        return [{'result':'正常終了','error':''}]
    
    def __create_2rentan_odds_file(place):
        """scrapingされた2連単csvファイルのデータ作成
        Args:
            place string:競艇場
        Returns:
            dict: 処理結果
        """
        race_no = BoatRaceUtils.get_race_no(place)
        bet_type = '2'
        #print(race_no)
        if race_no == '0':
            return [{'result':'レース期間外','error':'no_element'}]
        
        result = []
        if place == 'ashiya':
            result = BoatRaceUtils.__create_ashiya_2rentan_odds_file(place,race_no,bet_type)
        if place == 'omura':
            result = BoatRaceUtils.__create_omura_2rentan_odds_file(place,race_no,bet_type)
        if place == 'tokuyama':
            result = BoatRaceUtils.__create_tokuyama_2rentan_odds_file(place,race_no,bet_type)

        if not result or not result['error']:
            BoatRaceUtils.__marge_odds_file(place,bet_type)
        return [{'result':'正常終了','error':''}]

    def __get_ashiya_race_no():
        """芦屋競艇レース順取得
        Returns:
            string: レース順
        """
        
        for i in range(1,13):
            load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?day=" + BoatRaceUtils.today + "&race=" + str(i)
            #html = requests.get(load_url,verify=False)
            #soup = BeautifulSoup(html.content, "html.parser")
            with urllib.request.urlopen(load_url) as response:
                html = response.read()
            soup = BeautifulSoup(html, "html.parser",from_encoding="utf-8")
            if soup.find_all("div",attrs={"class": "category-odds"}) and not soup.find_all("div",attrs={"class": "sorry_info"}):
                return str(i)
        return '0'

    def __get_omura_race_no():
        """大村競艇レース順取得
        Returns:
            string: レース順
        """
        for i in range(1,13):
            load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds.php?day=" + BoatRaceUtils.today + "&race=1&race=" + str(i)
            #html = requests.get(load_url,verify=False)
            #soup = BeautifulSoup(html.content, "html.parser")
            with urllib.request.urlopen(load_url) as response:
                html = response.read()
            soup = BeautifulSoup(html, "html.parser",from_encoding="utf-8")
            if soup.find_all("img",attrs={"id": "weitimg"}):
                return '0'
            if not soup.find_all("span",attrs={"class": "endodds"}):
                return str(i)
        return '0'

    def __get_tokuyama_race_no():
        """徳山競艇レース順取得
        Returns:
            string: レース順
        """
        for i in range(1,13):
            load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?day=" + BoatRaceUtils.today + "&race=" + str(i)
            #html = requests.get(load_url,verify=False)
            #soup = BeautifulSoup(html.content, "html.parser")
            with urllib.request.urlopen(load_url) as response:
                html = response.read()
            soup = BeautifulSoup(html, "html.parser",from_encoding="utf-8")
            if soup.find_all("div",attrs={"class": "category-odds"}):
                return str(i)
        return '0'
        

    def __create_ashiya_3rentan_odds_file(place,race_no):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
        Returns:
            dict: 処理結果
        """
        load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?day=" + BoatRaceUtils.today + "&race="+race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        if not soup.find_all("div",attrs={"class": "category-odds"}):
            print("[レース期間外]対象の要素がありませんでした")
            return [{'result':'レース期間外','error':'no_element'}]

        all_table = soup.find_all("table")
            
        if len(all_table) > 7 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]

        csv_path = BoatRaceUtils.__get_odds_csv(place)
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            
            for i, table in enumerate(all_table, 0):
                rows = []
                if table.find_all("td", attrs={"class": "odd_color"}):
                    rows=table.find_all("td", class_=['odd_color', 'even_color'])
                for row in rows:
                    writer.writerow([row.get_text()])
        return {'result':'正常終了','error':''}

    def __create_ashiya_2rentan_odds_file(place,race_no,bet_type='2'):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """

        load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?page=group-odds-result.php&day=" + BoatRaceUtils.today + "&kind=Odds2&race="+race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        if not soup.find_all("div",attrs={"class": "category-odds"}):
            print("[レース期間外]対象の要素がありませんでした")
            return [{'result':'レース期間外','error':'no_element'}]

        all_table = soup.find_all("table")
        if len(all_table) > 11 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]
        
        result = [{'result':'正常終了','error':''}]

        csv_path = BoatRaceUtils.__get_odds_csv(place,bet_type)
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            
            for i, table in enumerate(all_table, 0):
                rows = []
                if i == 6:
                    return result
                if table.find_all("td", attrs={"class": "odds"}):
                    rows=table.find_all("td", class_=['odds'])
                for row in rows:
                    writer.writerow([row.get_text()])
        return result

    def __create_omura_3rentan_odds_file(place,race_no,bet_type='3'):
        """大村競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds.php?day=" + BoatRaceUtils.today + "&race=1&race=" + race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        all_table = soup.find_all("table")
            
        if len(all_table) > 7 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]
        
        csv_path = BoatRaceUtils.__get_odds_csv(place,bet_type)
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            
            #最初の行は余計なので削除
            all_table.pop(0)
            for i, table in enumerate(all_table, 0):
                # oddsを指定
                rows = table.find_all("td", attrs={"class": "oddsitem"})
                for row in rows:
                    writer.writerow([row.get_text()])
        return [{'result':'正常終了','error':''}]
    
    def __create_omura_2rentan_odds_file(place,race_no,bet_type='2'):
        """大村競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds2.php?day=" + BoatRaceUtils.today + "&race=" + race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        all_table = soup.find_all("table", attrs={"class": "tblodds"})
        if len(all_table) > 7 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]
        
        csv_path = BoatRaceUtils.__get_odds_csv(place,bet_type)
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            
            #最初の行は余計なので削除
            all_table.pop(-1)
            for i, table in enumerate(all_table, 0):
                # oddsを指定
                rows = table.find_all("td", attrs={"class": "oddsitem"})
                for row in rows:
                    writer.writerow([row.get_text()])
        return [{'result':'正常終了','error':''}]

    def __create_tokuyama_3rentan_odds_file(place,race_no,bet_type=const_path.BET_3TAN):
        """徳山競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        
        load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?day=" + BoatRaceUtils.today + "&race=" + race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        all_table = soup.find_all("table")
            
        if len(all_table) > 6 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]

        csv_path = BoatRaceUtils.__get_odds_csv(place,bet_type)

        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            
            for i, table in enumerate(all_table, 0):
                # oddsを指定
                rows = table.find_all("td", attrs={"class": "odds"})
                for row in rows:
                    writer.writerow([row.get_text()])
        return [{'result':'正常終了','error':''}]

    def __create_tokuyama_2rentan_odds_file(place,race_no,bet_type='2'):
        """徳山競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?page=group-odds-result.php&day=" + BoatRaceUtils.today + "&race=" + race_no + "&kind=Odds2"
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")

        all_table = soup.find_all("table")

        if len(all_table) > 11 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]
        #後ろ5つは2連複なので削除
        del all_table[6:]
        
        csv_path = BoatRaceUtils.__get_odds_csv(place,bet_type)
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)

            #all_table = all_table[:-5]
            for i, table in enumerate(all_table, 0):
                # oddsを指定
                rows = table.find_all("td", attrs={"class": "odds"})
                for row in rows:
                    writer.writerow([row.get_text()])
        return [{'result':'正常終了','error':''}]

    def __marge_odds_file(place,bet_type='3'):
        """scrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            bet_type string :買い方
        """
        # パスで指定したファイルの一覧をリスト形式で取得. （ここでは一階層下のtestファイル以下）

        race_order_csv_path = BoatRaceUtils.__get_odds_race_order_csv(bet_type)
        odds_csv_path = BoatRaceUtils.__get_odds_csv(place,bet_type)
        
        csv_files_list = [race_order_csv_path,odds_csv_path]
        #csv_files_list = []
        #csv_files_list_append = csv_files_list.append
        #csv_files_list_append(race_order_csv_path)
        #csv_files_list_append(odds_csv_path)      
        
        #csvファイルの中身を追加していくリストを用意
        data_list = []
        data_list_append = data_list.append
        
        #読み込むファイルのリストを走査
        for file in csv_files_list:
            data_list_append(pd.read_csv(file))
        
        #リストを全て行方向に結合
        #axis=0:行方向に結合, sort
        df = pd.concat(data_list, axis=1, sort=True)
        marge_csv_path = BoatRaceUtils.__get_marge_odds_csv(place,bet_type)
        df.to_csv(marge_csv_path,index=False)
    
    def __get_compose_odds(target_odds_list,toushigaku):
        """
        Args:
            target_odds_list list:計算対象データリスト
            bet_type toushigaku :投資金額
        Returns:
            list: 配当額他計算結果配列
        """        
        # 今回のレースで5つの舟券を3000円を予算として購入する場合、オッズが2.5/3.6/7.8/15.0/50.0の場合、合成オッズは以下のように計算します。
        #1÷(1÷2.5＋1÷3.6＋1÷7.8＋1÷15.0＋1÷50.0)＝1.12
        compose_odds = 0
        compose_odds_list = []
        compose_odds_list_append = compose_odds_list.append

        #for float_row in float_odds_list:
        for target_row in target_odds_list:
            odds_row = round(1/float(target_row['odds']),2)
            compose_odds_list_append(odds_row)
            compose_odds += odds_row
        compose_odds = round(1/compose_odds,2)
    
        #合成オッズは1.12倍です。
        # 予算の3,000円×1.12倍＝3,360円が理論利益金額です。
        # 選択数が1個の場合投資額 * 1.35とする
        if len(compose_odds_list) == 1:
            rironkingaku = float(toushigaku) * 1.5
        else:
            rironkingaku = float(toushigaku) * compose_odds
        #print(rironkingaku)
    
        toushigaku_list = []
        toushigaku_list_append = toushigaku_list.append

        max_toushigaku = 0
        #for stb_row in float_odds_list:
        for target_row in target_odds_list:
            __toushigaku = BoatRaceUtils.__round_tens_place(round(rironkingaku/float(target_row['odds']),2))
            toushigaku_list_append(__toushigaku)
            max_toushigaku += __toushigaku
        #max_toushigaku = sum(toushigaku_list)
        #print(max_toushigaku)

        while int(toushigaku) < int(max_toushigaku):
            __max_toushigaku_idx_list = [i for i, v in enumerate(toushigaku_list) if v == max(toushigaku_list)]
            for idx in __max_toushigaku_idx_list:
                toushigaku_list[idx] = toushigaku_list[idx] - 100
            max_toushigaku = sum(toushigaku_list)
        #print(toushigaku_list)

        #result = []
        for i,target_row in enumerate(target_odds_list):
            __each_investment_money = toushigaku_list[i]
            #BoatRaceUtils.__round_tens_place(round(rironkingaku/float(target_row['odds']),2))
            __tekityuukingaku = math.floor(__each_investment_money * float(target_row['odds']))
            target_odds_list[i]["each_investment_money"] = str(__each_investment_money)
            target_odds_list[i]["tekityuukingaku"] = str(__tekityuukingaku)
            target_odds_list[i]["profit"] = str(__tekityuukingaku - int(toushigaku))
            #result.append(target_row)
        #print(result)
        return target_odds_list
    
    def __mobius_equation(target_odds_list,toushigaku):
        """
        :params target_odds_list: 計算対象データリスト
        :type target_odds_list: list
        """
        result = []
        ##（1）まず買いたい馬券のオッズを書き出して、一番低いオッズをほかのオッズで割っていく
        #例　5.7倍　10.2倍　7.8倍　23.6倍　50.2倍であれば、一番低いのは5.7倍
        #5.7÷10.2=0.56（小数第二位四捨五入）
        #5.7÷7.8=0.73
        #5.7÷23.6=0.24
        #5.7÷50.2=0.11
        min_odds = 1.0
        stb_odds_list = []
        stb_calc_list = []
        for target_row in target_odds_list:
            stb_odds_list.append(float(target_row['odds']))
        min_odds = min(stb_odds_list)
    
        for val in stb_odds_list:
            if min_odds != val:
                stb_calc_list.append(round(min_odds/val,2))
    
        print("（1）まず買いたい馬券のオッズを書き出して、一番低いオッズをほかのオッズで割っていく")
        print(stb_calc_list)
    
        ##（2） これらすべてを足して、さらに1を足す
        stb_ratio = 1.0
        for val in stb_calc_list:
            stb_ratio += val
        print("（2） これらすべてを足して、さらに1を足す")
        print(round(stb_ratio,3))
    
        ##（3）一番低いオッズの券の投資金を求める。計算は、それまでの損失金×1.3÷（一番低いオッズ―比率数値）
        #15000×1.3÷（5.7－2.64）=6372.5=6400円（十の位を四捨五入）
        investment_money = (float(toushigaku) * 1.3)/(min_odds-stb_ratio)
        investment_money = round(math.floor(investment_money),-2)
    
        print("（3）一番低いオッズの券の投資金を求める。計算は、それまでの損失金×1.3÷（一番低いオッズ―比率数値）")
        print(investment_money)
    
        ##（4） 今回の仮の払戻金総額を求める。（3）で出した一番低い馬券の投資金×そのオッズ
        total_refund = math.floor(min_odds * investment_money)
        total_refund = BoatRaceUtils.__round_tens_place(total_refund)
        print("（4） 今回の仮の払戻金総額を求める。（3）で出した一番低い馬券の投資金×そのオッズ")
        print(total_refund)
        ##（5）その他の馬券の投資金を求める。計算式は　仮の払戻金総額÷それぞれの馬券のオッズ
        for target_row in target_odds_list:
            target_row["each_investment_money"] = math.ceil(total_refund/float(target_row['odds']))
            target_row["tekityuukingaku"] = target_row["each_investment_money"] * float(target_row['odds'])
            target_row["profit"] = investment_money*float(target_row['odds']) - float(toushigaku)
            result.append(target_row)
        return result
    
    def __round_tens_place(calc_val):
        """10の位で切り上げ切り下げを判定する
        Args:
            calc_val float :判定対象データ
        Returns:
            float: 処理結果
        """
        calc_val = BoatRaceUtils.__org_round(calc_val)
        s = str(calc_val)
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
