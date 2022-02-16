import copy
import sys
import io 
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import csv
import importlib
import datetime
from datetime import datetime as dt
from django.conf import settings
from bs4 import BeautifulSoup
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import logging
import pandas as pd
import numpy as np
import urllib
import lxml.html
import dask.dataframe as dd

import socket
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from logging import basicConfig, getLogger, DEBUG

from ..utils import common
from ..utils import boatrace
from ..logic import scrapingbatch

class BoatRaceBatchLogic:
    ## 開催日当日yyyymmdd
    today = dt.today().strftime("%Y%m%d")
    ## 環境ディレクトリ
    global const_path
    const_path = importlib.import_module(common.CommonUtils().get_const_path())
    ## logger
    logger = getLogger(__name__)

    def __init__(self, value=''):
        self.value = value
        

    def create_race_info_places_bk(self):
        """ 基本情報ファイルのバックアップを作成する
        """
        bk_csv_path = const_path.BOATRACE_BACE_INFO_CSV_BK
        csv_data_list = []
        try:
            csv_data = dd.read_csv(const_path.BOATRACE_BACE_INFO_CSV, header=None, encoding='utf_8').compute()
            csv_data_list = csv_data.values.tolist()
            #print(csv_data)
    
            if not os.path.exists(bk_csv_path):
                open(bk_csv_path, 'w')
            bk_csv_data = dd.read_csv(bk_csv_path, header=None, encoding='utf_8')
            
            csv_files_list = [csv_data,bk_csv_data]
            
            df = dd.concat(csv_files_list, axis=0, sort=True)
            df.to_csv(bk_csv_path,mode="a",header=False,index=False)
            print('success : create_race_info_places_bk')
        
        except pd.errors.EmptyDataError as e:
            #import traceback
            #traceback.print_exc()
            print("EmptyDataError: {} is empty ".format(e))
            with open(bk_csv_path, 'w',encoding="utf_8") as f:
                writer = csv.writer(f)
                for data_row in csv_data_list:
                    writer.writerow(data_row)
            print("success : CREATE BK FILE")

    def create_race_info_places(self,day):
        """ 開催レースをまとめて取得
        Args:
            day string:yyyymmdd
        Returns:
            list: レース開催情報まとめ
        """

        if day != self.today:
            print(day+' ; '+self.today)
            self.today = day
                
        result = []
        result_append = result.append

        jcds = ['12','17','18','19','21','24']

        urls= []
        for jcd in jcds:
            urls.append("https://www.boatrace.jp/owpc/pc/race/raceindex?jcd=" + jcd + "&hd=" + self.today)
        
        mapfunc = partial(requests.get, headers={'Referer' :'https://www.google.com/','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'})
        with ThreadPoolExecutor(4) as executor:
            url_response_results = list(executor.map(mapfunc, urls))

        for i,url_response_one in enumerate(url_response_results):
            stb = {'jcd':'','target_day':self.today,'place_name':'','title_name':''}

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
        
        
        csv_path = const_path.BOATRACE_BACE_INFO_CSV
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for data_row in result:
                writer.writerow(data_row.values())
        print('success : create_race_info_places')
        return result

    def create_odds_file_places(self,place,bet_type,race_no):
        """ 開催レースをまとめて取得
        Args:
            place string:競艇場
            bet_type string:
            race_no string:
        Returns:
            list: レース開催情報まとめ
        """
        if not boatrace.BoatRaceUtils.is_effect_place(place):
            return {'result':'レース場対象外','error':'no_place'}
        
        csv_data = dd.read_csv(const_path.BOATRACE_BACE_INFO_CSV, header=None, encoding='utf_8').compute()
        csv_data_list = csv_data.values.tolist()
        
        race_nos = []
        
        if place == 'all' and bet_type == '9':
            race_nos = boatrace.BoatRaceUtils.get_race_no_all()
            
            if len(race_nos) != 0:
                return self.__create_xrentan_odds_file_all(csv_data_list,race_nos)
            return {'result':'レース期間外','error':'no_element'}  
        return boatrace.BoatRaceUtils.create_xrentan_odds_file(place,bet_type,race_no)

  
    def __create_xrentan_odds_file_all(self,csv_data_list,race_nos):
        """scrapingされた2,3連単csvファイルのデータ作成
        Args:
            place string:競艇場
            race_no
            bet_type string:買い方
        Returns:
            dict: 処理結果
        """
        result = {'result':'初期対応','error':''}
        now_time = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        
        ccu = common.CommonUtils()
        sbl = scrapingbatch.ScrapingBatchLogic()

        for data_row in csv_data_list:
            start_date = ccu.time_minus_or_plus_one_ymdhm(data_row[4],-1)
            end_date   = ccu.time_minus_or_plus_one_ymdhm(data_row[5],0,15)
            place_no   = str(data_row[0])
            
            if ( start_date <= now_time and now_time <= end_date ):
                
                if place_no == '21' and race_nos['ashiya'] is not None:
                    result = sbl.create_ashiya_3rentan_odds_file('ashiya',race_nos['ashiya'])
                    result = sbl.create_ashiya_3renpuku_odds_file('ashiya',race_nos['ashiya'])
                    result = sbl.create_ashiya_2ren_odds_file('ashiya',race_nos['ashiya'],const_path.BET_2ALL)            
                if place_no == '24' and race_nos['omura'] is not None:
                    result = sbl.create_omura_3rentan_odds_file('omura',race_nos['omura'])
                    result = sbl.create_omura_3renpuku_odds_file('omura',race_nos['omura'])
                    result = sbl.create_omura_2ren_odds_file('omura',race_nos['omura'],const_path.BET_2ALL)
                if place_no == '18' and race_nos['tokuyama'] is not None:
                    result = sbl.create_tokuyama_3rentan_odds_file('tokuyama',race_nos['tokuyama'])
                    result = sbl.create_tokuyama_3renpuku_odds_file('tokuyama',race_nos['tokuyama'])
                    result = sbl.create_tokuyama_2ren_odds_file('tokuyama',race_nos['tokuyama'],const_path.BET_2ALL)
    
        return result

    def __create_xrentan_odds_file(self,place,race_no,bet_type):
        """scrapingされた2,3連単csvファイルのデータ作成
        Args:
            place string:競艇場
            race_no
            bet_type string:買い方
        Returns:
            dict: 処理結果
        """

        if race_no == '0':
            return {'result':'レース期間外','error':'no_element'}
    
        result = {'result':'初期対応','error':''}
        if place == 'ashiya' and bet_type == '3':
            result = self.__create_ashiya_3rentan_odds_file(place,race_no,bet_type)
        if place == 'ashiya' and bet_type == '2':
            result = self.__create_ashiya_2rentan_odds_file(place,race_no,bet_type)
        if place == 'omura' and bet_type == '3':
            result = self.__create_omura_3rentan_odds_file(place,race_no,bet_type)
        if place == 'omura' and bet_type == '2':
            result = self.__create_omura_2rentan_odds_file(place,race_no,bet_type)
        if place == 'tokuyama' and bet_type == '3':
            result = self.__create_tokuyama_3rentan_odds_file(place,race_no,bet_type)
        if place == 'tokuyama' and bet_type == '2':
            result = self.__create_tokuyama_2rentan_odds_file(place,race_no,bet_type)
        
        #if not result or not result['error']:
        #    BoatRaceUtils.__marge_odds_file(place)
    
        return result

    def __get_beautifulsoup_init(self,load_url):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            load_url string:指定URL
        Returns:
            dict: 処理結果
        """
        headers = {
            "Referer": "https://www.google.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
            }
        html = requests.get(load_url,verify=False,headers=headers)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
        return soup

    def __create_ashiya_3rentan_odds_file(self,place,race_no,bet_type='3'):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
        Returns:
            dict: 処理結果
        """
        load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?day=" + self.today + "&race="+race_no
        soup = self.__get_beautifulsoup_init(load_url)
    
        if not soup.find_all("div",attrs={"class": "category-odds"}):
            self.logger.debug("[レース期間外]対象の要素がありませんでした")
            return {'result':'レース期間外','error':'no_element'}

        all_table = soup.find_all("table")
            
        if len(all_table) > 7 or len(all_table) == 0:
            self.logger.debug("[table>7]対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}

        __3rentna_list = self.get_race_order_list(bet_type)

        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append

        for i, table in enumerate(all_table, 0):
            rows = []
            if table.find_all("td", attrs={"class": "odd_color"}):
                rows = table.find_all("td", class_=['odd_color', 'even_color'])
            for row in rows:
                __3rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.create_sorted_odds_list(__3rentna_list,__3rentan_odds)

        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
        
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for i, row in enumerate(all_data_list, 0):
                 writer.writerow(row)
        return {'result':'正常終了','error':''}

    def __create_ashiya_2rentan_odds_file(self,place,race_no,bet_type='2'):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """

        load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?page=group-odds-result.php&day=" + self.today + "&kind=Odds2&race="+race_no
        soup = self.__get_beautifulsoup_init(load_url)
    
        if not soup.find_all("div",attrs={"class": "category-odds"}):
            self.logger.debug("[レース期間外]対象の要素がありませんでした")
            return {'result':'レース期間外','error':'no_element'}

        all_table = soup.find_all("table")
        if len(all_table) > 11 or len(all_table) == 0:
            self.logger.debug("対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}
        
        __2rentna_list = self.get_race_order_list(bet_type)

        __2rentan_odds = []
        __2rentan_odds_append = __2rentan_odds.append
 
        for i, table in enumerate(all_table, 0):
            rows = []
            if i == 6:
                break
            # oddsを指定
            if table.find_all("td", attrs={"class": "odds"}):
                rows=table.find_all("td", class_=['odds'])
            for row in rows:
                __2rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.create_sorted_odds_list(__2rentna_list,__2rentan_odds)
        
        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)

        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for i, row in enumerate(all_data_list, 0):
                 writer.writerow(row)

        return {'result':'正常終了','error':''}

    def __create_omura_3rentan_odds_file(self,place,race_no,bet_type='3'):
        """大村競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds.php?day=" + self.today + "&race=1&race=" + race_no
        soup = self.__get_beautifulsoup_init(load_url)
    
        all_table = soup.find_all("table")
            
        if len(all_table) > 7 or len(all_table) == 0:
            self.logger.debug("対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}
        #最初の行は余計なので削除
        all_table.pop(0)
        
        __3rentna_list = self.get_race_order_list(bet_type)

        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append

        for i, table in enumerate(all_table, 0):
            # oddsを指定
            rows = table.find_all("td", attrs={"class": "oddsitem"})
            for row in rows:
                __3rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.create_sorted_odds_list(__3rentna_list,__3rentan_odds)

        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)

        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for i, row in enumerate(all_data_list, 0):
                 writer.writerow(row)
        return {'result':'正常終了','error':''}
    
    def __create_omura_2rentan_odds_file(self,place,race_no,bet_type='2'):
        """大村競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds2.php?day=" + self.today + "&race=" + race_no
        soup = self.__get_beautifulsoup_init(load_url)
    
        all_table = soup.find_all("table", attrs={"class": "tblodds"})
        if len(all_table) > 7 or len(all_table) == 0:
            self.logger.debug("対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}
        #最初の行は余計なので削除
        all_table.pop(-1)
        
        __2rentna_list = self.get_race_order_list(bet_type)

        __2rentan_odds = []
        __2rentan_odds_append = __2rentan_odds.append

        for i, table in enumerate(all_table, 0):
            # oddsを指定
            rows = table.find_all("td", attrs={"class": "oddsitem"})
            for row in rows:
                __2rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.create_sorted_odds_list(__2rentna_list,__2rentan_odds)
        
        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)

        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for i, row in enumerate(all_data_list, 0):
                 writer.writerow(row)
        return {'result':'正常終了','error':''}

    def __create_tokuyama_3rentan_odds_file(self,place,race_no,bet_type='3'):
        """徳山競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        
        load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?day=" + self.today + "&race=" + race_no
        soup = self.__get_beautifulsoup_init(load_url)
    
        all_table = soup.find_all("table")
            
        if len(all_table) > 6 or len(all_table) == 0:
            self.logger.debug("対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}

        __3rentna_list = self.get_race_order_list(bet_type)

        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append

        for i, table in enumerate(all_table, 0):
            rows = table.find_all("td", attrs={"class": "odds"})
            for row in rows:
                __3rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.create_sorted_odds_list(__3rentna_list,__3rentan_odds)

        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for i, row in enumerate(all_data_list, 0):
                 writer.writerow(row)
        #with open(csv_path, 'w',encoding="utf_8") as f:
        #    writer = csv.writer(f)
        #    
        #    for i, table in enumerate(all_table, 0):
        #        # oddsを指定
        #        rows = table.find_all("td", attrs={"class": "odds"})
        #        for row in rows:
        #            writer.writerow([row.get_text()])
        return {'result':'正常終了','error':''}

    def __create_tokuyama_2rentan_odds_file(self,place,race_no,bet_type='2'):
        """徳山競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?page=group-odds-result.php&day=" + self.today + "&race=" + race_no + "&kind=Odds2"
        soup = self.__get_beautifulsoup_init(load_url)

        all_table = soup.find_all("table")

        if len(all_table) > 11 or len(all_table) == 0:
            self.logger.debug("対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}
        #後ろ5つは2連複なので削除
        del all_table[6:]

        __2rentna_list = self.get_race_order_list(bet_type)

        __2rentan_odds = []
        __2rentan_odds_append = __2rentan_odds.append

        for i, table in enumerate(all_table, 0):
            rows = table.find_all("td", attrs={"class": "odds"})
            for row in rows:
                __2rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.create_sorted_odds_list(__2rentna_list,__2rentan_odds)
        
        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)

        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for i, row in enumerate(all_data_list, 0):
                 writer.writerow(row)

        return {'result':'正常終了','error':''}

    def get_race_order_list(self,bet_type):
        """
        Args:
            bet_type string:買い方
        Returns:
            dict: csvファイルの辞書型データ
        """
        __3rentna_list = [
            [1,123],[2,124],[3,125],[4,126],
            [5,132],[6,134],[7,135],[8,136],
            [9,142],[10,143],[11,145],[12,146],
            [13,152],[14,153],[15,154],[16,156],
            [17,162],[18,163],[19,164],[20,165],
            [21,213],[22,214],[23,215],[24,216],
            [25,231],[26,234],[27,235],[28,236],
            [29,241],[30,243],[31,245],[32,246],
            [33,251],[34,253],[35,254],[36,256],
            [37,261],[38,263],[39,264],[40,265],
            [41,312],[42,314],[43,315],[44,316],
            [45,321],[46,324],[47,325],[48,326],
            [49,341],[50,342],[51,345],[52,346],
            [53,351],[54,352],[55,354],[56,356],
            [57,361],[58,362],[59,364],[60,365],
            [61,412],[62,413],[63,415],[64,416],
            [65,421],[66,423],[67,425],[68,426],
            [69,431],[70,432],[71,435],[72,436],
            [73,451],[74,452],[75,453],[76,456],
            [77,461],[78,462],[79,463],[80,465],
            [81,512],[82,513],[83,514],[84,516],
            [85,521],[86,523],[87,524],[88,526],
            [89,531],[90,532],[91,534],[92,536],
            [93,541],[94,542],[95,543],[96,546],
            [97,561],[98,562],[99,563],[100,564],
            [101,612],[102,613],[103,614],[104,615],
            [105,621],[106,623],[107,624],[108,625],
            [109,631],[110,632],[111,634],[112,635],
            [113,641],[114,642],[115,643],[116,645],
            [117,651],[118,652],[119,653],[120,654]
            ]
        __3renpuku_list = [
            [1,123],[2,124],[3,125],[4,126],
            [5,134],[6,135],[7,136],
            [8,145],[9,146],
            [10,156],
            [11,234],[12,235],[13,236],
            [14,245],[15,246],
            [16,256],
            [17,345],[18,346],
            [19,356],
            [20,456]
            ]
        __2rentna_list = [
            [1,12],[2,13],[3,14],[4,15],[5,16],
            [6,21],[7,23],[8,24],[9,25],[10,26],
            [11,31],[12,32],[13,34],[14,35],[15,36],
            [16,41],[17,42],[18,43],[19,45],[20,46],
            [21,51],[22,52],[23,53],[24,54],[25,56],
            [26,61],[27,62],[28,63],[29,64],[30,65]
            ]
        __2renpuku_list = [
            [1,12],[2,13],[3,14],[4,15],[5,16],
            [6,23],[7,24],[8,25],[9,26],
            [10,34],[11,35],[12,36],
            [13,45],[14,46],
            [15,56]
            ]
        if bet_type == const_path.BET_2TAN:
            return __2rentna_list
        if bet_type == const_path.BET_2PUKU:
            return __2renpuku_list
        if bet_type == const_path.BET_3PUKU:
            return __3renpuku_list
        return __3rentna_list
 
    def create_sorted_odds_list(self,__xrentna_list,__xrentan_odds):
        """
        Args:
            __xrentna_list list :レース順list
            __xrentan_odds list :オッズlist
            sort_param dict     :ソート情報
        Returns:
            list: 3行目昇順でソートした2次元配列
        """
        reverse_flag = False
        
        for i in range(len(__xrentna_list)):
            __xrentna_list[i].extend(__xrentan_odds[i])
        return sorted(__xrentna_list, reverse=reverse_flag, key=self.__keyfunc)#key=lambda x: x[2])
    
    def __keyfunc(self,x):
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

    def __keyfunc_d1(self,x):
        """sorted用のkey 1列目でソートしfloatを数値順にstrは無限にする
        Args:
            x list[]:ソート対象の2次元配列
        Returns:
            float:ソート用に変換したfloat値
        """
        if type(x[1]) == float and x[1] != 0.0:
            return x[1]
        elif type(x[1]) == float and x[1] == 0.0:
            return float('inf')
        else:
            return float('inf')

    def __time_minus_or_plus_one_ymdhm(self,time_str: str,add_time = 0,add_second = 0) -> str:
        """
        時間を元に1時間マイナスした値にし日付＋時間で返す
        Args:
            time_str str   : hh:mm形式の文字列時間
            add_time str   : 操作したい時
            add_second str : 操作したい分
        Returns:
            str:yyyymmdd hh:mm形式のマイナスされた時間
        """
        now_ymd = dt.today().strftime("%Y%m%d")
        #時間型に変換する
        #print(type(time_str))
        #print("id(time_str) = %s" % id(time_str))
        conv_time = dt.strptime(now_ymd+' '+time_str, '%Y%m%d %H:%M')
        #print(conv_time)
        return str(conv_time + datetime.timedelta(hours=add_time,seconds=add_second))