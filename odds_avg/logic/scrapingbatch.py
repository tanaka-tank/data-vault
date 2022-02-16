import sys
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

import traceback
import logging
import urllib
import lxml.html

from concurrent.futures import ThreadPoolExecutor
from functools import partial
from logging import basicConfig, getLogger, DEBUG

from ..utils import common
from ..utils import boatrace
from . import boatracebatch
from ..conf import const

class ScrapingBatchLogic:
    ## 開催日当日yyyymmdd
    today = dt.today().strftime("%Y%m%d")
    ## 環境ディレクトリ
    global const_path
    const_path = importlib.import_module(common.CommonUtils().get_const_path())
    ## logger
    logger = getLogger(__name__)
    ## ボートバッチロジック生成
    brbl = None

    def __init__(self, value=''):
        self.value = value
        self.brbl = boatracebatch.BoatRaceBatchLogic()
        
    def create_race_info_places(self,day):
        """ 開催レースをまとめて取得
        Args:
            day string:yyyymmdd
        Returns:
            list: レース開催情報まとめ
        """

        if day != self.today:
            self.today = day
                
        result = []
        result_append = result.append

        jcds = boatrace.BoatRaceUtils.get_jcd_cd_all()

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

    def create_race_deadline_time(self,day):
        """ 締切予定時刻をまとめて取得
        Args:
            day string:yyyymmdd
        Returns:
            list: レース締切予定時刻まとめ
        """

        if day != self.today:
            self.today = day
                
        result = []
        result_append = result.append

        jcds = boatrace.BoatRaceUtils.get_jcd_cd_all()

        urls= []
        for jcd in jcds:
            urls.append("https://www.boatrace.jp/owpc/pc/race/raceindex?jcd=" + jcd + "&hd=" + self.today)
        
        mapfunc = partial(requests.get, headers={'Referer' :'https://www.google.com/','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'})
        with ThreadPoolExecutor(4) as executor:
            url_response_results = list(executor.map(mapfunc, urls))

        for i,url_response_one in enumerate(url_response_results):
            stb = {
                'jcd':'',
                'target_day':self.today,
                'place_name':''
                }

            soup = BeautifulSoup(url_response_one.content, "html.parser",from_encoding="utf-8")
            lxml_coverted_data = lxml.html.fromstring(str(soup))
            
            if len(lxml_coverted_data.xpath('/html/body/main/div/div/div/div[1]/h2/span')) != 0:
                continue
            stb['jcd'] = jcds[i]
            stb['place_name'] = lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[1]/div/div[1]/img/@alt)')
            stb['deadline_times'] = [
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[1]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[2]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[3]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[4]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[5]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[6]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[7]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[8]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[9]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[10]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[11]/tr/td[2])'),
                lxml_coverted_data.xpath('string(/html/body/main/div/div/div/div[2]/div[3]/table/tbody[12]/tr/td[2])')
            ]
            
            result_append(stb)
        
        csv_path = const_path.BOATRACE_DEADLINE_TIMES_CSV
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for data_row in result:
                writer.writerow(data_row.values())
        print('success : create_race_deadline_time')
        return result
    
    def create_ashiya_3rentan_odds_file(self,place,race_no,bet_type=const_path.BET_3TAN):
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

        __3rentna_list = self.brbl.get_race_order_list(bet_type)

        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append

        for table in all_table:
            rows = []
            if table.find_all("td", attrs={"class": "odd_color"}):
                rows = table.find_all("td", class_=['odd_color', 'even_color'])
            for row in rows:
                __3rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.brbl.create_sorted_odds_list(__3rentna_list,__3rentan_odds)

        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
        
        self.__writerow_csv(csv_path,all_data_list)

        return {'result':'正常終了','error':''}

    def create_ashiya_3renpuku_odds_file(self,place,race_no,bet_type=const_path.BET_3PUKU):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
        Returns:
            dict: 処理結果
        """
        load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?day=" + self.today + "&kind=Odds3&race="+race_no
        soup = self.__get_beautifulsoup_init(load_url)
    
        if not soup.find_all("div",attrs={"class": "str3Fuk"}):
            self.logger.debug("[レース期間外]対象の要素がありませんでした")
            return {'result':'レース期間外','error':'no_element'}


        all_table = soup.find_all("table",attrs={"class": "odds3Fuk"})
            
        if len(all_table) > 4 or len(all_table) == 0:
            self.logger.debug("[table>4]対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}

        __3puku_list = self.brbl.get_race_order_list(bet_type)

        __3puku_odds = []
        __3puku_odds_append = __3puku_odds.append

        for table in all_table:
            rows = []
            if table.find_all("td", attrs={"class": "odd_color"}):
                rows = table.find_all("td", class_=['odd_color', 'even_color'])
            for row in rows:
                __3puku_odds_append([float(row.get_text())])
        
        all_data_list = self.brbl.create_sorted_odds_list(__3puku_list,__3puku_odds)

        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
        
        self.__writerow_csv(csv_path,all_data_list)

        return {'result':'正常終了','error':''}
    
    def create_ashiya_2ren_odds_file(self,place,race_no,bet_type=const_path.BET_2TAN):
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
        
        if bet_type == const_path.BET_2TAN or bet_type == const_path.BET_2ALL:
            stb_bet_type = const_path.BET_2TAN
            all_table = soup.find_all("table",attrs={"class": "odds2Tan"})
            if len(all_table) > 6 or len(all_table) == 0:
                self.logger.debug("対象の要素がありませんでした")
                return {'result':'[table>6]対象の要素がありませんでした2tan','error':'no_element'}
            
            __2rentna_list = self.brbl.get_race_order_list(stb_bet_type)
    
            __2rentan_odds = []
            __2rentan_odds_append = __2rentan_odds.append
     
            for table in all_table:
                rows = []
                if table.find_all("td", attrs={"class": "odds"}):
                    rows = table.find_all("td", class_=['odds'])
                for row in rows:
                    __2rentan_odds_append([float(row.get_text())])
            
            all_data_list = self.brbl.create_sorted_odds_list(__2rentna_list,__2rentan_odds)
            
            csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(stb_bet_type,place,race_no)
    
            self.__writerow_csv(csv_path,all_data_list)

        if bet_type == const_path.BET_2PUKU or bet_type == const_path.BET_2ALL:
            stb_bet_type = const_path.BET_2PUKU
            all_table = soup.find_all("table",attrs={"class": "odds2Fuk"})
            if len(all_table) > 5 or len(all_table) == 0:
                self.logger.debug("対象の要素がありませんでした")
                return {'result':'[table>6]対象の要素がありませんでした2puku','error':'no_element'}
            
            __2puku_list = self.brbl.get_race_order_list(stb_bet_type)
    
            __2puku_odds = []
            __2puku_odds_append = __2puku_odds.append
     
            for table in all_table:
                rows = []
                if table.find_all("td", attrs={"class": "odds"}):
                    rows = table.find_all("td", class_=['odds'])
                for row in rows:
                    __2puku_odds_append([float(row.get_text())])
            
            all_data_list = self.brbl.create_sorted_odds_list(__2puku_list,__2puku_odds)
            
            csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(stb_bet_type,place,race_no)
    
            self.__writerow_csv(csv_path,all_data_list)

        return {'result':'正常終了','error':''}

    def create_omura_3rentan_odds_file(self,place,race_no,bet_type=const_path.BET_3TAN):
        """大村競艇の3連単scrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds.php?day=" + self.today + "&race=" + race_no
        soup = self.__get_beautifulsoup_init(load_url)
    
        #all_table = soup.find_all("table")

        all_table = soup.find("table",attrs={"class":"tblodds_full"}).find_all("table")
        if len(all_table) > 7 or len(all_table) == 0:
            self.logger.debug("[table>7]対象の要素がありませんでした")
            return {'result':'[table>7]対象の要素がありませんでした','error':'no_element'}
        #最初の行は余計なので削除
        #all_table.pop(0)
        
        __3rentna_list = self.brbl.get_race_order_list(bet_type)

        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append

        for table in all_table:
            # oddsを指定
            rows = table.find_all("td", attrs={"class": "oddsitem"})
            for row in rows:
                __3rentan_odds_append([float(row.get_text())])
        
        all_data_list = self.brbl.create_sorted_odds_list(__3rentna_list,__3rentan_odds)

        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)

        self.__writerow_csv(csv_path,all_data_list)

        return {'result':'正常終了','error':''}

    def create_omura_3renpuku_odds_file(self,place,race_no,bet_type=const_path.BET_3PUKU):
        """大村競艇の3連複scrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds3.php?day=" + self.today + "&race=" + race_no
        soup = self.__get_beautifulsoup_init(load_url)
        
        try:
            all_table = soup.find("div",attrs={"id":"tbloddsrf3"}).find_all("table",attrs={"class":"tblodds"})

            if len(all_table) > 1 or len(all_table) == 0:
                alert_str = "[table->"+str(len(all_table))+"]対象の要素がありませんでした3puku"
                self.logger.warning(alert_str)
                return {'result':alert_str,'error':'no_element'}
            
            __3puku_list = self.brbl.get_race_order_list(bet_type)
    
            __3puku_odds = []
            __3puku_odds_append = __3puku_odds.append
    
            for table in all_table:
                # oddsを指定
                rows = table.find_all("td", attrs={"class": "oddsitem"})
                for row in rows:
                    __3puku_odds_append([float(row.get_text())])
            
            all_data_list = self.brbl.create_sorted_odds_list(__3puku_list,__3puku_odds)
    
            csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
            
            self.__writerow_csv(csv_path,all_data_list)

        except AttributeError as e:
            traceback.print_exc()
            self.logger.error(e)
            return {'result':'システムエラー['+sys._getframe().f_code.co_name+']','error':e}
        return {'result':'正常終了','error':''}

    def create_omura_2ren_odds_file(self,place,race_no,bet_type=const_path.BET_2TAN):
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

        try:
            if bet_type == const_path.BET_2TAN or bet_type == const_path.BET_2ALL:
                stb_bet_type = const_path.BET_2TAN
                
                all_table = soup.find("div",attrs={"id":"tbloddsrt"}).find_all("table",attrs={"class":"tblodds"})
                
                if len(all_table) > 7 or len(all_table) == 0:
                    alert_str = "[table->"+str(len(all_table))+"]対象の要素がありませんでした2tan"
                    self.logger.warning(alert_str)
                    return {'result':alert_str,'error':'no_element'}
                
                __2tna_list = self.brbl.get_race_order_list(stb_bet_type)
        
                __2tan_odds = []
                __2tan_odds_append = __2tan_odds.append
        
                for table in all_table:
                    # oddsを指定
                    rows = table.find_all("td", attrs={"class": "oddsitem"})
                    for row in rows:
                        __2tan_odds_append([float(row.get_text())])
                
                all_data_list = self.brbl.create_sorted_odds_list(__2tna_list,__2tan_odds)
                
                csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(stb_bet_type,place,race_no)
        
                self.__writerow_csv(csv_path,all_data_list)
    
            if bet_type == const_path.BET_2PUKU or bet_type == const_path.BET_2ALL:
                stb_bet_type = const_path.BET_2PUKU
                all_table = soup.find("div",attrs={"id": "tbloddsrf"}).find_all_next("table",attrs={"class": "tblodds"})
                
                if len(all_table) > 1 or len(all_table) == 0:
                    alert_str = "[table->"+str(len(all_table))+"]対象の要素がありませんでした2puku"
                    self.logger.warning(alert_str)
                    return {'result':alert_str,'error':'no_element'}
                
                __2puku_list = self.brbl.get_race_order_list(stb_bet_type)
        
                __2puku_odds = []
                __2puku_odds_append = __2puku_odds.append
        
                for table in all_table:
                    # oddsを指定
                    rows = table.find_all("td", attrs={"class": "oddsitem"})
                    for row in rows:
                        __2puku_odds_append([float(row.get_text())])
                
                all_data_list = self.brbl.create_sorted_odds_list(__2puku_list,__2puku_odds)
                
                csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(stb_bet_type,place,race_no)
                self.__writerow_csv(csv_path,all_data_list)

        except AttributeError as e:
            traceback.print_exc()
            self.logger.error(e)
            return {'result':'システムエラー['+sys._getframe().f_code.co_name+']','error':e}
        return {'result':'正常終了','error':''}

    def create_tokuyama_3rentan_odds_file(self,place,race_no,bet_type=const_path.BET_3TAN):
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
    
        try:
            #all_table = soup.find_all("table")
            all_table = soup.find("div",attrs={"class":"str3Tan"}).find_all("table",attrs={"class":"odds3Tan"})
                
            if len(all_table) > 6 or len(all_table) == 0:
                alert_str = "[table->"+str(len(all_table))+"]対象の要素がありませんでした3tan"
                self.logger.warning(alert_str)
                return {'result':alert_str,'error':'no_element'}
    
            __3rentna_list = self.brbl.get_race_order_list(bet_type)
    
            __3rentan_odds = []
            __3rentan_odds_append = __3rentan_odds.append
    
            for table in all_table:
                rows = table.find_all("td", attrs={"class": "odds"})
                for row in rows:
                    __3rentan_odds_append([float(row.get_text())])
            
            all_data_list = self.brbl.create_sorted_odds_list(__3rentna_list,__3rentan_odds)
    
            csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
            self.__writerow_csv(csv_path,all_data_list)

        except AttributeError as e:
            traceback.print_exc()
            self.logger.error(e)
            return {'result':'システムエラー['+sys._getframe().f_code.co_name+']','error':e}
        return {'result':'正常終了','error':''}

    def create_tokuyama_3renpuku_odds_file(self,place,race_no,bet_type=const_path.BET_3PUKU):
        """徳山競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            dict: 処理結果
        """
        
        load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?day=" + self.today + "&race=" + race_no + '&kind=Odds3'
        soup = self.__get_beautifulsoup_init(load_url)
    
        try:
            all_table = soup.find("div",attrs={"class":"str3Fuk"}).find_all("table",attrs={"class":"odds3Fuk"})
                
            if len(all_table) > 4 or len(all_table) == 0:
                alert_str = "[table->"+str(len(all_table))+"]対象の要素がありませんでした3tan"
                self.logger.warning(alert_str)
                return {'result':alert_str,'error':'no_element'}
    
            __3renpuku_list = self.brbl.get_race_order_list(bet_type)
    
            __3renpuku_odds = []
            __3renpuku_odds_append = __3renpuku_odds.append
    
            for table in all_table:
                rows = table.find_all("td", attrs={"class": "odds"})
                for row in rows:
                    __3renpuku_odds_append([float(row.get_text())])
            
            all_data_list = self.brbl.create_sorted_odds_list(__3renpuku_list,__3renpuku_odds)
    
            csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
            self.__writerow_csv(csv_path,all_data_list)

        except AttributeError as e:
            traceback.print_exc()
            self.logger.error(e)
            return {'result':'システムエラー['+sys._getframe().f_code.co_name+']','error':e}
        return {'result':'正常終了','error':''}

    def create_tokuyama_2ren_odds_file(self,place,race_no,bet_type=const_path.BET_2TAN):
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

        try:
            if bet_type == const_path.BET_2TAN or bet_type == const_path.BET_2ALL:
                stb_bet_type = const_path.BET_2TAN
                all_table = soup.find("div",attrs={"class":"str2Tan"}).find_all("table",attrs={"class":"odds2Tan"})
                #all_table = soup.find_all("table")
        
                if len(all_table) > 6 or len(all_table) == 0:
                    alert_str = "[table->"+str(len(all_table))+"]対象の要素がありませんでした2tan"
                    self.logger.warning(alert_str)
                    return {'result':alert_str,'error':'no_element'}
        
                __2tna_list = self.brbl.get_race_order_list(stb_bet_type)
        
                __2tan_odds = []
                __2tan_odds_append = __2tan_odds.append
        
                for table in all_table:
                    rows = table.find_all("td", attrs={"class": "odds"})
                    for row in rows:
                        __2tan_odds_append([float(row.get_text())])
                
                all_data_list = self.brbl.create_sorted_odds_list(__2tna_list,__2tan_odds)
                
                csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(stb_bet_type,place,race_no)
        
                self.__writerow_csv(csv_path,all_data_list)

            if bet_type == const_path.BET_2PUKU or bet_type == const_path.BET_2ALL:
                stb_bet_type = const_path.BET_2PUKU
                all_table = soup.find("div",attrs={"class":"str2Fuk"}).find_all("table",attrs={"class":"odds2Fuk"})
                #all_table = soup.find_all("table")
        
                if len(all_table) > 6 or len(all_table) == 0:
                    alert_str = "[table->"+str(len(all_table))+"]対象の要素がありませんでした2tan"
                    self.logger.warning(alert_str)
                    return {'result':alert_str,'error':'no_element'}
        
                __2puku_list = self.brbl.get_race_order_list(stb_bet_type)
        
                __2puku_odds = []
                __2puku_odds_append = __2puku_odds.append
        
                for table in all_table:
                    rows = table.find_all("td", attrs={"class": "odds"})
                    for row in rows:
                        __2puku_odds_append([float(row.get_text())])
                
                all_data_list = self.brbl.create_sorted_odds_list(__2puku_list,__2puku_odds)
                
                csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(stb_bet_type,place,race_no)

                self.__writerow_csv(csv_path,all_data_list)

        except AttributeError as e:
            traceback.print_exc()
            self.logger.error(e)
            return {'result':'システムエラー['+sys._getframe().f_code.co_name+']','error':e}
        return {'result':'正常終了','error':''}

    def __get_beautifulsoup_init(self,load_url):
        """scrapingの初期化情報
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

    def __writerow_csv(self,csv_path,all_data_list):
        """csv書き込み
        Args:
            csv_path string : 指定CSVフルパス
            all_data_list list[list] : 書き込みデータ
        """
        with open(csv_path, 'w',encoding="utf_8") as f:
            writer = csv.writer(f)
            for row in all_data_list:
                 writer.writerow(row)