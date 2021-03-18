import csv
import os
import re
import importlib
from datetime import datetime as dt
from . import utils

class AmazonCoinLogic:
    global const_path
    const_path = importlib.import_module(utils.Utils.get_const_path())

    def __init__(self, value=''):
        self.value = value

    def get_amazon_coin_data_rows_data(self,xyear=''):
        """scrapingされたcsvファイルのデータ取得
        Args:
            xyear string: 
        Returns:
            dict: csvファイルの辞書型データ
        """
        file_list = self.__get_amazon_coin_data_csv(xyear)

        row_list = []
        row_list_append = row_list.append
        
        for row in file_list:
            #print(row)
            row_list_append(utils.Utils.convert_ymd(row))
        convert_rows = {};
        convert_rows.setdefault('rows', row_list)
        convert_rows.setdefault('yearly_list', self.get_amazon_coin_data_yearly_list())
        return convert_rows
    
    def get_amazon_coin_data_chart1_data(self,year=''):
        """chart1y用のデータ取得
        Returns:
            dict: csvファイルの辞書型データ
        """
        file_list = self.__get_amazon_coin_data_csv(year)
        return self.__convert_calum(file_list)

    def get_amazon_coin_data_yearly_list(self):
        """データ取得
        Returns:
            dict: csvファイルの辞書型データ
        """

        files = os.listdir(const_path.AMAZON_COIN_DATA_CSV_PATH)
        row_list = []
        row_list_append = row_list.append

        for one_file_name in files:
            if one_file_name.startswith(const_path.AMAZON_COIN_DATA_CSV_FILE_NAME):
                row_list_append(re.search("(?<=amazon_coin_data_).*(?=\.csv)",one_file_name).group())
        return sorted(row_list, reverse=True)

    def get_amazon_coin_data_yyyy_csv_full_path(self,xyear=''):
        """年次別amazoncoin_csvファイルの環境変数を見てファイルのフルパスを返す
        Args:
            xyear string: 
        Returns:
            str:ファイルのフルパス
        """
        if not xyear:
            xyear = dt.today().strftime("%Y")
        
        full_path = const_path.AMAZON_COIN_DATA_CSV_PATH + const_path.AMAZON_COIN_DATA_CSV_FILE_NAME + xyear+ '.csv'
        return full_path

    def get_amazon_coin_data_csv_full_path(self):
        """全一覧amazoncoin_csvファイルの環境変数を見てファイルのフルパスを返す
        Returns:
            str:ファイルのフルパス
        """
        
        full_path = const_path.AMAZON_COIN_DATA_CSV_PATH + const_path.AMAZON_COIN_DATA_CSV__ALL_FILE_NAME
        return full_path

    def __get_amazon_coin_data_csv(self,xyear=''):
        """amazoncoin_csvファイルの環境変数を見て取得する
        Args:
            xyear string: 
        Returns:
            csv.reader object list:csv情報の配列
        """
        if not xyear:
            xyear = dt.today().strftime("%Y")
        
        full_path = self.get_amazon_coin_data_yyyy_csv_full_path(xyear)
        csv_file = open(full_path, "r", encoding="utf-8", errors="", newline="" )
        file_list = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        return file_list
    
    def __convert_calum(self,file_list):
        """
        Args:
            file_list _csv.reader object: 変換対象配列(full想定)
        Returns:
            dict:変換後配列
        """
        convert_rows = {'hiduke':[],'500yen':[],'1000yen':[],'2500yen':[],'5000yen':[],'10000yen':[],'50000yen':[]}

        for row in file_list:
            convert_rows['hiduke'].append(utils.Utils.convert_slash(row[0]))
            convert_rows['500yen'].append(row[1])
            convert_rows['1000yen'].append(row[2])
            convert_rows['2500yen'].append(row[3])
            convert_rows['5000yen'].append(row[4])
            convert_rows['10000yen'].append(row[5])
            convert_rows['50000yen'].append(row[6])
        return convert_rows