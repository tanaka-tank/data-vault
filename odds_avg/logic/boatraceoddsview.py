import os
os.environ["OMP_NUM_THREADS"] = "1" # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = "1" # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "1" # export MKL_NUM_THREADS=6
os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "1" # export NUMEXPR_NUM_THREADS=6
import importlib
from datetime import datetime as dt
import json
import csv
#import dask.dataframe as dd
from logging import getLogger

from ..utils import common
from ..utils import boatrace

class BoatRaceOddsViewLogic:
    ## 開催日当日yyyymmdd
    today = dt.today().strftime("%Y%m%d")
    ## 環境ディレクトリ
    global const_path
    const_path = importlib.import_module(common.CommonUtils().get_const_path())
    
    ## logger
    logger = getLogger("file")

    def __init__(self, value=''):
        self.value = value
    
    def get_race_info_all_place(self,day):
        """ 開催レースをまとめて取得
        Args:
            day string:yyyymmdd
        Returns:
            list: レース開催情報まとめ
        """
        result = [{'get_day':self.today}]
        result_append = result.append

        if day != self.today and '1'<=dt.today().strftime("%H").lstrip('0'):
            self.today = day
            result = [{'get_day':self.today}]
        #print(result)
        
        csv_file = open(const_path.BOATRACE_BACE_INFO_CSV, 'r', encoding='utf_8', errors='', newline='')
        f = csv.reader(csv_file, delimiter=',', doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        csv_data_list = f

        #csv_data = dd.read_csv(const_path.BOATRACE_BACE_INFO_CSV, header=None, encoding='utf_8').compute()
        #csv_data_list = csv_data.values.tolist()

        for row in csv_data_list:
            stb = {
                'jcd':row[0],
                'target_day':row[1],
                'place_name':row[2],
                'title_name':row[3],
                'start_time':row[4],
                'end_time':row[5]
                }
            result_append(stb)

        return result
    
    def get_init_params(self,place,bet_type):
        """初期情報作成
        Args:
            place string :競艇場
            bet_type string :買い方
        Returns:
            list: 初期値データ群
        """

        day = dt.today().strftime("%Y%m%d")
        
        if day != self.today and '1'<= dt.today().strftime("%H"):
            dt.today = day
        try:
            today_full = dt.today().strftime('%Y%m%d%H%M%S%f')[:-3]
            race_no_and_deadline_time = boatrace.BoatRaceUtils.get_race_no_csv_relative(place)
            race_no = race_no_and_deadline_time['race_no']
            
            params = {
                'title_name':boatrace.BoatRaceUtils.get_place_name(place),
                'now_date':'',
                'race_no': '',
                'race_deadline_time': '',
                'get_last_time' : ''
            }
            if race_no == '0':
                #self.logger.error( 'レース期間外： ')
                return common.CommonUtils.power_merge_dict_d2(params,{'result':'レース期間外[30分前から確認できます]','error':'no_element'})
                
            params['now_date'] = today_full
            params['race_no'] = race_no
            params['race_deadline_time'] = race_no_and_deadline_time['race_deadline_time']
            
            csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
            if not os.path.isfile(csv_path):
                import sys
                return {'result':"Wait...[オッズ関連情報待ち]",'error':sys._getframe().f_code.co_name }

            params['get_last_time'] = boatrace.BoatRaceUtils.get_odds_file_update_time(csv_path)

            odds_list = self.__get_new_race_odds_data_dict(place,bet_type,race_no)
            params['odds_list'] = odds_list
            
            #csv_file = open(csv_path, 'r', encoding='utf_8', errors='', newline='')
            #f = csv.reader(csv_file, delimiter=',', doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
            #params['odds_list'] = f

            #csv_data = dd.read_csv(csv_path, header=None, encoding='utf_8',dtype = 'str').compute()
            #params['odds_list'] = csv_data.values.tolist()
            
        except Exception as e:
            message = 'システムエラー[初期情報]'
            self.logger.error(message + '： {}'.format(e))
            return {'result': message, 'error':e}
        return params

    def get_post_data_params(self,req,place,bet_type,upd_flag=''):
        """更新情報作成
        Args:
            req WSGIRequest list.dist :入力データ
            place string :競艇場
            bet_type string :買い方
            upd_flag string:更新のみ処理フラグ
        Returns:
            dict: 入力結果計算データ
        """
        
        race_no_and_deadline_time = boatrace.BoatRaceUtils.get_race_no_csv_relative(place)
        race_no = race_no_and_deadline_time['race_no']

        order_param = {'order_zyun':'asc','order_type':'sort_odds'}

        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)
        if req.POST['race_no'] != race_no:
            params = {'result':'レース時間超過','error':'time_over'}
            
            params['get_last_time'] = boatrace.BoatRaceUtils.get_odds_file_update_time(csv_path)

            csv_file = open(csv_path, 'r', encoding='utf_8', errors='', newline='')
            f = csv.reader(csv_file, delimiter=',', doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
            params['odds_list'] = f
            #csv_data = dd.read_csv(csv_path, header=None, encoding='utf_8',dtype = 'str').compute()
            #params['odds_list'] = csv_data.values.tolist()
            
            return params
        
        
        result = {
            'toushigaku':req.POST["toushigaku"],
            'race_deadline_time': race_no_and_deadline_time['race_deadline_time'],
            'get_last_time':boatrace.BoatRaceUtils.get_odds_file_update_time(csv_path)
        }

        req_data_json = req.POST['post_data_json']
        req_data = json.loads(req_data_json)
        orth_target_odds_list = []
        for target_odds_row in req_data['target_odds_list']:
            orth_target_odds_list.append(json.loads(target_odds_row))

        order_param = boatrace.BoatRaceUtils.get_sort_column_num(req)
        
        try:
            if upd_flag != '1':
                result['odds_list'] = self.__get_calc_odds_data(place,race_no,orth_target_odds_list,result['toushigaku'],bet_type,order_param)
            if upd_flag == '1':
                result['odds_list'] = self.get_new_odds_data(place,race_no,orth_target_odds_list,bet_type,order_param)
        except KeyError as e:
            message = 'レース期間外'
            self.logger.error(message + '： {}'.format(e))
            return result.update({'result':'レース期間外','error':'time_out : {}'.format(e)})

        return result

    def get_new_odds_data(self,place,race_no,target_odds_list,bet_type,order_param):
        """scrapingされたオッズデータ取得
        Args:
            place string:競艇場
            race_no
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
        
        new_odds_list = self.__get_new_race_odds_data_dict(place,bet_type,race_no,order_param)

        for base_row in new_odds_list:
            add_flag = 0
            for target_row in target_odds_list: 
                if str(target_row['odds_no']) == str(base_row[0]):
                    base_row += ['checked']
                    change_list_append(base_row)
                    add_flag = 1
            if add_flag == 0:
                change_list_append(base_row)
        return change_list

    def __get_new_race_odds_data_dict(self,place,bet_type,race_no,order_param={'order_zyun':'','order_type':''}):
        """ソートされたオッズデータ群の取得
        Args:
            place string:競艇場
            bet_type string:買い方
            race_no string:レース番号
            order_param dict:ソート情報
        Returns:
            dict: csvファイルの辞書型データ
        """
        csv_path = boatrace.BoatRaceUtils.get_odds_file_full_path(bet_type,place,race_no)

        csv_file = open(csv_path, 'r', encoding='utf_8', errors='', newline='')
        csv_data = csv.reader(csv_file, delimiter=',', doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        lines = list(csv_data)
        #print(lines)
        #csv_data = dd.read_csv(csv_path, header=None, encoding='utf_8',dtype = {0:str,1:int}).compute()
        #print(csv_data)
        return common.CommonUtils.get_sorted_odds_list(lines,order_param)
    
    def __get_calc_odds_data(self,place,race_no,target_odds_list,toushigaku,bet_type,order_param):
        """scrapingされたオッズデータ取得
        Args:
            place string:競艇場
            race_no
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

        new_odds_list= self.__get_new_race_odds_data_dict(place,bet_type,race_no,order_param)

        for base_row in new_odds_list:
            for target_row in target_odds_list: 
                if str(target_row['odds_no']) == str(base_row[0]):
                    calc_list_append(base_row)
        
        calc_list2d = self.__get_compose_odds_list2d(calc_list,toushigaku)

        for i,base_row in enumerate(new_odds_list):
            for calc_change_row in calc_list2d: 
                if str(calc_change_row[0]) == str(base_row[0]):
                    new_odds_list[i] = calc_change_row

        return new_odds_list


    def __get_compose_odds_list2d(self,target_odds_list,toushigaku):
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
            if round(1/float(target_row[2]),2) == 0.0:
                odds_row = 0.1
            else:
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

        toushigaku_list = []
        toushigaku_list_append = toushigaku_list.append

        max_toushigaku = 0

        for target_row in target_odds_list:
            __toushigaku = common.CommonUtils.round_tens_value(round(rironkingaku/float(target_row[2]),2))
            toushigaku_list_append(__toushigaku)
            max_toushigaku += __toushigaku
        
        while int(toushigaku) < int(max_toushigaku):
            __max_toushigaku_idx_list = [i for i, v in enumerate(toushigaku_list) if v == max(toushigaku_list)]
            for idx in __max_toushigaku_idx_list:
                toushigaku_list[idx] = toushigaku_list[idx] - 100
            max_toushigaku = sum(toushigaku_list)

        #result = []
        import math
        for i,target_row in enumerate(target_odds_list):
            __each_investment_money = toushigaku_list[i]
            #BoatRaceUtils.__round_tens_value(round(rironkingaku/float(target_row['odds']),2))
            __tekityuukingaku = math.floor(__each_investment_money * float(target_row[2]))
            target_odds_list[i] += [str(__each_investment_money)]
            target_odds_list[i] += [str(__tekityuukingaku)]
            target_odds_list[i] += [str(__tekityuukingaku - int(toushigaku))]
            #result.append(target_row)
        return target_odds_list