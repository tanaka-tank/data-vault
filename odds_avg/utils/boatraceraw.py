import os
import operator
import importlib
import datetime
from datetime import datetime
from django.conf import settings
from bs4 import BeautifulSoup
import requests
import math
import numpy as np
import urllib
import socket
from . import common
from . import boatrace


class BoatRaceRawUtils:
    ## 開催日当日yyyymmdd
    today = datetime.today().strftime("%Y%m%d")
    
    origGetAddrInfo = socket.getaddrinfo
    def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
        return BoatRaceRawUtils.origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

    def __init__(self, value=''):
        self.value = value
        socket.getaddrinfo = self.getAddrInfoWrapper

    def get_odds_xrentan_data_list_origin(place,bet_type='3',order_param={'order_zyun':'','order_type':''}):
        """scrapingされた3連単のオッズデータ取得
        Args:
            place string:競艇場
            bet_type string:買い方
            order_param dict:ソート順
        Returns:
            dict: 辞書型データ
        """
        day = datetime.today().strftime("%Y%m%d")
        if day != BoatRaceRawUtils.today:
            BoatRaceRawUtils.today = day

        if not boatrace.BoatRaceUtils.is_effect_place(place):
            return [{'result':'レース場対象外','error':'no_place'}]
        
        socket.getaddrinfo = BoatRaceRawUtils.getAddrInfoWrapper
        return BoatRaceRawUtils.__get_xrentan_odds_list(place,order_param,bet_type)

    
    def get_calc_odds_data(place,target_odds_list,toushigaku,bet_type,order_param):
        """scrapingされたオッズデータ取得
        Args:
            place string:競艇場
            target_odds_list list:計算対象データリスト
            toushigaku string:投資金額
            bet_type string:買い方
            order_param dict:ソート情報
        Returns:
            dict: csvファイルの辞書型データ
        """
        if not boatrace.BoatRaceUtils.is_effect_place(place):
            return [{'result':'レース場対象外','error':'no_place'}]
        
        calc_list = []
        calc_list_append = calc_list.append
        new_list= BoatRaceRawUtils.get_odds_xrentan_data_list_origin(place,bet_type,order_param)
        for base_row in new_list:
            for target_row in target_odds_list: 
                if str(target_row['odds_no']) == str(base_row[0]):
                    calc_list_append(base_row)
        #print(stbchange_list)
        calc_list2d = BoatRaceRawUtils.__get_compose_odds_list2d(calc_list,toushigaku)
        for i,base_row in enumerate(new_list):
            for stbchange_row in calc_list2d: 
                if str(stbchange_row[0]) == str(base_row[0]):
                    new_list[i] = stbchange_row
        #print(new_list)
        
        #change_list = []
        #change_list_append = change_list.append
        #target_odds_list = BoatRaceRawUtils.__get_compose_odds(target_odds_list,toushigaku)
        #for base_row in BoatRaceRawUtils.get_odds_xrentan_data_list_origin(place,bet_type,order_param):
        #    add_flag = 0
        #    for target_row in target_odds_list: 
        #        if str(target_row['odds_no']) == str(base_row[0]):
        #            stb = list(target_row.values())
        #            stb[2] = base_row[2]
        #            print(target_row.values())
        #            change_list_append(stb)
        #            add_flag = 1
        #    if add_flag == 0:
        #        change_list_append(base_row)
        #return change_list
        return new_list
    
    def get_new_odds_data(place,target_odds_list,bet_type,order_param):
        """scrapingされたオッズデータ取得
        Args:
            place string:競艇場
            target_odds_list list:計算対象データリスト
            bet_type string:買い方
            order_param
        Returns:
            dict: csvファイルの辞書型データ
        """
        if not boatrace.BoatRaceUtils.is_effect_place(place):
            return [{'result':'レース場対象外','error':'no_place'}]
        change_list = []
        change_list_append = change_list.append
        
        for base_row in BoatRaceRawUtils.get_odds_xrentan_data_list_origin(place,bet_type,order_param):
            add_flag = 0
            for target_row in target_odds_list: 
                if str(target_row['odds_no']) == str(base_row[0]):
                    #base_row.append('checked')
                    base_row += ['checked']
                    change_list_append(base_row)
                    add_flag = 1
            if add_flag == 0:
                change_list_append(base_row)
        return change_list
    
    def __get_xrentan_odds_list(place,order_param,bet_type):
        """scrapingされた2or3連単データ取得
        Args:
            place string:競艇場
            order_param
            bet_type
        Returns:
            dict: 処理結果
        """
        race_no = boatrace.BoatRaceUtils.get_race_no(place)
        #print(race_no)
        if race_no == '0':
            return [{'result':'レース期間外','error':'no_element'}]

        result = []
        if place == 'ashiya' and bet_type == '3':
            result = BoatRaceRawUtils.__get_ashiya_3rentan_odds_list(race_no,bet_type,order_param)
        if place == 'ashiya' and bet_type == '2':
            result = BoatRaceRawUtils.__get_ashiya_2rentan_odds_list(race_no,bet_type,order_param)
        if place == 'omura' and bet_type == '3':
            result = BoatRaceRawUtils.__get_omura_3rentan_odds_list(race_no,bet_type,order_param)
        if place == 'omura' and bet_type == '2':
            result = BoatRaceRawUtils.__get_omura_2rentan_odds_list(race_no,bet_type,order_param)
        if place == 'tokuyama' and bet_type == '3':
            result = BoatRaceRawUtils.__get_tokuyama_3rentan_odds_list(race_no,bet_type,order_param)
        if place == 'tokuyama' and bet_type == '2':
            result = BoatRaceRawUtils.__get_tokuyama_2rentan_odds_list(race_no,bet_type,order_param)
    
        return result
        
    def __get_ashiya_3rentan_odds_list(race_no,bet_type,order_param):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
        Returns:
            list: 処理結果
        """
        load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?day=" + BoatRaceRawUtils.today + "&race="+race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        if not soup.find_all("div",attrs={"class": "category-odds"}):
            print("[レース期間外]対象の要素がありませんでした")
            return [{'result':'レース期間外','error':'no_element'}]

        all_table = soup.find_all("table")
            
        if len(all_table) > 7 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return {'result':'対象の要素がありませんでした','error':'no_element'}

        __3rentna_list = BoatRaceRawUtils.__get_race_order_list(bet_type)

        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append

        for i, table in enumerate(all_table, 0):
            rows = []
            if table.find_all("td", attrs={"class": "odd_color"}):
                rows=table.find_all("td", class_=['odd_color', 'even_color'])
            for row in rows:
                __3rentan_odds_append([float(row.get_text())])

        return BoatRaceRawUtils.__create_sorted_odds_list(__3rentna_list,__3rentan_odds,order_param)

    def __get_ashiya_2rentan_odds_list(race_no,bet_type,order_param):
        """芦屋競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            list: 処理結果
        """

        load_url = "https://www.boatrace-ashiya.com/modules/yosou/group-odds-result.php?page=group-odds-result.php&day=" + BoatRaceRawUtils.today + "&kind=Odds2&race="+race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        if not soup.find_all("div",attrs={"class": "category-odds"}):
            print("[レース期間外]対象の要素がありませんでした")
            return [{'result':'レース期間外','error':'no_element'}]

        all_table = soup.find_all("table")
        if len(all_table) > 11 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]

        __2rentna_list = BoatRaceRawUtils.__get_race_order_list(bet_type)
        __2rentan_odds = []
        __2rentan_odds_append = __2rentan_odds.append

        for i, table in enumerate(all_table, 0):
            rows = []
            if i == 6:
                break
            if table.find_all("td", attrs={"class": "odds"}):
                rows=table.find_all("td", class_=['odds'])
            for row in rows:
                __2rentan_odds_append([float(row.get_text())])
        
        return BoatRaceRawUtils.__create_sorted_odds_list(__2rentna_list,__2rentan_odds,order_param)

    def __get_omura_3rentan_odds_list(race_no,bet_type,order_param):
        """大村競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            list: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds.php?day=" + BoatRaceRawUtils.today + "&race=1&race=" + race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        all_table = soup.find_all("table")
        
        if len(all_table) > 7 or len(all_table) == 0:
            print(all_table)
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]

        #return {'result':'正常終了','error':''}
        __3rentna_list = BoatRaceRawUtils.__get_race_order_list(bet_type)
        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append
        all_table.pop(0)
        for i, table in enumerate(all_table, 0):
            # oddsを指定
            rows = table.find_all("td", attrs={"class": "oddsitem"})
            for row in rows:
                __3rentan_odds_append([float(row.get_text())])
        
        return BoatRaceRawUtils.__create_sorted_odds_list(__3rentna_list,__3rentan_odds,order_param)
    
    def __get_omura_2rentan_odds_list(race_no,bet_type,order_param):
        """大村競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            list: 処理結果
        """
        load_url = "https://omurakyotei.jp/yosou/include/new_top_iframe_odds2.php?day=" + BoatRaceRawUtils.today + "&race=" + race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        all_table = soup.find_all("table", attrs={"class": "tblodds"})
        if len(all_table) > 7 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]
        
        #最初の行は余計なので削除
        all_table.pop(-1)

        __2rentna_list = BoatRaceRawUtils.__get_race_order_list(bet_type)
        __2rentan_odds = []
        __2rentan_odds_append = __2rentan_odds.append

        for i, table in enumerate(all_table, 0):
            # oddsを指定
            rows = table.find_all("td", attrs={"class": "oddsitem"})
            for row in rows:
                __2rentan_odds_append([float(row.get_text())])
        
        return BoatRaceRawUtils.__create_sorted_odds_list(__2rentna_list,__2rentan_odds,order_param)

    def __get_tokuyama_3rentan_odds_list(race_no,bet_type,order_param):
        """徳山競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            list: 処理結果
        """
        
        load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?day=" + BoatRaceRawUtils.today + "&race=" + race_no
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")
    
        all_table = soup.find_all("table")
            
        if len(all_table) > 6 or len(all_table) == 0:
            print(all_table)
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]

        __3rentna_list = BoatRaceRawUtils.__get_race_order_list(bet_type)
        __3rentan_odds = []
        __3rentan_odds_append = __3rentan_odds.append
        for i, table in enumerate(all_table, 0):
            # oddsを指定
            rows = table.find_all("td", attrs={"class": "odds"})
            for j,row in enumerate(rows,0):
                __3rentan_odds_append([float(row.get_text())])
        
        return BoatRaceRawUtils.__create_sorted_odds_list(__3rentna_list,__3rentan_odds,order_param)

    def __get_tokuyama_2rentan_odds_list(race_no,bet_type,order_param):
        """徳山競艇のscrapingされたcsvファイルのデータ取得
        Args:
            place string:競艇場
            race_no string:レースの順番
            bet_type string :買い方
        Returns:
            list: 処理結果
        """
        load_url = "https://www.boatrace-tokuyama.jp/modules/yosou/group-odds-result.php?page=group-odds-result.php&day=" + BoatRaceRawUtils.today + "&race=" + race_no + "&kind=Odds2"
        html = requests.get(load_url,verify=False)
        soup = BeautifulSoup(html.content, "html.parser",from_encoding="utf-8")

        all_table = soup.find_all("table")

        if len(all_table) > 11 or len(all_table) == 0:
            print("対象の要素がありませんでした")
            return [{'result':'対象の要素がありませんでした','error':'no_element'}]
        #後ろ5つは2連複なので削除
        del all_table[6:]
        
        __2rentna_list = BoatRaceRawUtils.__get_race_order_list(bet_type)
        __2rentan_odds = []
        __2rentan_odds_append = __2rentan_odds.append

        for i, table in enumerate(all_table, 0):
            # oddsを指定
            rows = table.find_all("td", attrs={"class": "odds"})
            for row in rows:
                __2rentan_odds_append([float(row.get_text())])
        
        return BoatRaceRawUtils.__create_sorted_odds_list(__2rentna_list,__2rentan_odds,order_param)
    
    def __get_compose_odds(target_odds_list,toushigaku):
        """
        Args:
            target_odds_list list.dict:計算対象データリスト
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
        # 選択数が1個の場合投資額 * 1.25とする
        if len(compose_odds_list) == 1:
            threshold_value = 1.25
            if compose_odds < 3:
                threshold_value = 1.1
            if compose_odds >= 7:
                threshold_value = 1.5
            rironkingaku = float(toushigaku) * threshold_value
        else:
            rironkingaku = float(toushigaku) * compose_odds
        #print(rironkingaku)
        
       #_odds_list = []
       #_odds_list_append = _odds_list.append

        #for float_row in float_odds_list:
        #for target_row in target_odds_list:
        #    _odds_list_append(int(float(target_row['odds'])*10))
        #from math import gcd
        #x = np.array(_odds_list)
        #print(_odds_list)
        #print(BoatRaceRawUtils.lcmm(*_odds_list))
        #saisyoukoubaisu = BoatRaceRawUtils.lcmm(*_odds_list)
        #toushigaku_stb_list = []
        #toushigaku_stb_list_append = toushigaku_stb_list.append
        #for target_row in target_odds_list:
        #    __toushigaku = BoatRaceRawUtils.__round_tens_power_value(float(toushigaku)/float(target_row['odds']))
        #    toushigaku_stb_list_append(__toushigaku)
        #print(toushigaku_stb_list)

        toushigaku_list = []
        toushigaku_list_append = toushigaku_list.append

        max_toushigaku = 0
        #for stb_row in float_odds_list:
        for target_row in target_odds_list:
            #print((saisyoukoubaisu/int(float(target_row['odds'])*10))/10)
            #print( math.floor(((saisyoukoubaisu/int(float(target_row['odds'])*10))/10)/100) * 100 )
            __toushigaku = BoatRaceRawUtils.__round_tens_value(round(rironkingaku/float(target_row['odds']),2))
            toushigaku_list_append(__toushigaku)
            max_toushigaku += __toushigaku
        #max_toushigaku = sum(toushigaku_list)
        print(toushigaku_list)
        #toushigaku_list = toushigaku_stb_list
        

        while int(toushigaku) < int(max_toushigaku):
            __max_toushigaku_idx_list = [i for i, v in enumerate(toushigaku_list) if v == max(toushigaku_list)]
            for idx in __max_toushigaku_idx_list:
                toushigaku_list[idx] = toushigaku_list[idx] - 100
            max_toushigaku = sum(toushigaku_list)
        #print(toushigaku_list)

        #result = []
        for i,target_row in enumerate(target_odds_list):
            __each_investment_money = toushigaku_list[i]
            #BoatRaceUtils.__round_tens_value(round(rironkingaku/float(target_row['odds']),2))
            __tekityuukingaku = math.floor(__each_investment_money * float(target_row['odds']))
            target_odds_list[i]["each_investment_money"] = str(__each_investment_money)
            target_odds_list[i]["tekityuukingaku"] = str(__tekityuukingaku)
            target_odds_list[i]["profit"] = str(__tekityuukingaku - int(toushigaku))
            #result.append(target_row)
        #print(result)
        return target_odds_list

    def __get_compose_odds_list2d(target_odds_list,toushigaku):
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
            odds_row = round(1/float(target_row[2]),2)
            compose_odds_list_append(odds_row)
            compose_odds += odds_row
        compose_odds = round(1/compose_odds,2)
    
        #合成オッズは1.12倍です。
        # 予算の3,000円×1.12倍＝3,360円が理論利益金額です。
        # 選択数が1個の場合投資額 * 1.25とする
        if len(compose_odds_list) == 1:
            threshold_value = 1.25
            if compose_odds < 3:
                threshold_value = 1.1
            if compose_odds >= 7:
                threshold_value = 1.5
            rironkingaku = float(toushigaku) * threshold_value
        else:
            rironkingaku = float(toushigaku) * compose_odds
        #print(rironkingaku)

        toushigaku_list = []
        toushigaku_list_append = toushigaku_list.append

        max_toushigaku = 0

        for target_row in target_odds_list:
            __toushigaku = BoatRaceRawUtils.__round_tens_value(round(rironkingaku/float(target_row[2]),2))
            toushigaku_list_append(__toushigaku)
            max_toushigaku += __toushigaku

        print(toushigaku_list)
        
        while int(toushigaku) < int(max_toushigaku):
            __max_toushigaku_idx_list = [i for i, v in enumerate(toushigaku_list) if v == max(toushigaku_list)]
            for idx in __max_toushigaku_idx_list:
                toushigaku_list[idx] = toushigaku_list[idx] - 100
            max_toushigaku = sum(toushigaku_list)
        #print(toushigaku_list)

        #result = []
        for i,target_row in enumerate(target_odds_list):
            __each_investment_money = toushigaku_list[i]
            #BoatRaceUtils.__round_tens_value(round(rironkingaku/float(target_row['odds']),2))
            __tekityuukingaku = math.floor(__each_investment_money * float(target_row[2]))
            target_odds_list[i] += [str(__each_investment_money)]
            target_odds_list[i] += [str(__tekityuukingaku)]
            target_odds_list[i] += [str(__tekityuukingaku - int(toushigaku))]
            #result.append(target_row)
        #print(result)
        return target_odds_list

    def lcm(x, y):
        from math import gcd
        return x * y // gcd(x, y)
    def lcmm(*args):
        """https://qastack.jp/programming/147515/least-common-multiple-for-3-or-more-numbers
        Return lcm of args."""   
        from functools import reduce
        return reduce(BoatRaceRawUtils.lcm, args)
    
    def __round_tens_value(calc_val):
        """10の位で切り上げ切り下げを判定する
        Args:
            calc_val float :判定対象データ
        Returns:
            float: 処理結果
        """
        calc_val = BoatRaceRawUtils.__org_round(calc_val)
        s = str(calc_val)
        if s[-2] == '0' or s[-2] == '1' or s[-2] == '2'or s[-2] == '3'or s[-2] == '4':
            return math.floor(calc_val/100) * 100
        else:
            return math.ceil(calc_val/100) * 100
    
    def __round_tens_power_value(calc_val):
        """10の位で切り上げ切り下げを判定する
        Args:
            calc_val float :判定対象データ
        Returns:
            float: 処理結果
        """
        calc_val = BoatRaceRawUtils.__org_round(calc_val)
        return math.ceil(calc_val/100) * 100
    
    def __org_round(a:np.ndarray) -> np.ndarray:
        """正しく丸めるround
        ((a%1)==0.5)*(a//1%2==0)がやっていることとしては(a%1)==0.5で*.5の形になっているところだけに1が立つarrayを作り, 
        a//1%2==0で整数部分が偶数になっているところだけに1が立つarrayを作ってそれらをかけることで, (偶数).5 になっているところにだけ1を足すような愚直な方法になっています。
        このやり方は(pythonでは遅いと言われる)for文を使わないので、forを使って愚直にやるより若干の速さの改善が見込まれます。
        """
        rounded_a = np.round(a)+(((a%1)==0.5)*(a//1%2==0))
        return int(rounded_a)

    def __create_sorted_odds_list(__xrentna_list,__xrentan_odds,sort_param):
        """
        Args:
            __xrentna_list list:レース順list
            __xrentan_odds list:オッズlist
            sort_param dict:ソート情報
        Returns:
            list: 3行目昇順でソートした2次元配列
        """
        reverse_flag = False
        if sort_param['order_zyun'] == 'asc':
            reverse_flag = False
        if sort_param['order_zyun'] == 'desc':
            reverse_flag = True

        order_type_keyfunc = BoatRaceRawUtils.__keyfunc
        if sort_param['order_type'] == 'sort_odds':
            order_type_keyfunc = BoatRaceRawUtils.__keyfunc
        if sort_param['order_type'] == 'sort_funaban':
            order_type_keyfunc = BoatRaceRawUtils.__keyfunc_d1
        
        for i in range(len(__xrentna_list)):
            __xrentna_list[i].extend(__xrentan_odds[i])
        return sorted(__xrentna_list, reverse=reverse_flag, key=order_type_keyfunc)#key=lambda x: x[2])
    
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

    def __keyfunc_d1(x):
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

    def __get_race_order_list(bet_type):
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

        __2rentna_list = [
            [1,12],[2,13],[3,14],[4,15],[5,16],
            [6,21],[7,23],[8,24],[9,25],[10,26],
            [11,31],[12,32],[13,34],[14,35],[15,36],
            [16,41],[17,42],[18,43],[19,45],[20,46],
            [21,51],[22,52],[23,53],[24,54],[25,56],
            [26,61],[27,62],[28,63],[29,64],[30,65]
            ]
        if bet_type == '2':
            return __2rentna_list
        return __3rentna_list