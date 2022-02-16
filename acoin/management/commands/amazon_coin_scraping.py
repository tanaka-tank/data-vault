from django.core.management.base import BaseCommand
import argparse
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt
import time
import re
import random
from logging import getLogger
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from ... import amazoncoinlogic

class Command(BaseCommand):
    ## ロジッククラス読込
    global acl
    acl = amazoncoinlogic.AmazonCoinLogic()
    # [python manage.py help sampleBatch]で表示されるメッセージ
    #help = 'これはテスト用のコマンドバッチです'
    ## logger
    global logger
    logger = getLogger("file")

    #def add_arguments(self, parser):
    #    # コマンドライン引数を指定
    #    parser.add_argument('-t', action='store', dest='intValue', help='【必須】1,2,3,4から好きな数字を選んでください',required=True, type=valid_type)

    def handle(self, *args, **options):
        try:
            #ユーザーエージェントの設定（設定必須）
            headers = {
               "User-Agent": get_random_ua(),
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
               "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
               "CLIENT-IP": "8.8.8.8",
               "X-REAL-IP": "8.8.8.8",
               "X-FORWARDED-FOR": "8.8.8.8",
               "Content-type": "text/html;charset=utf-8",
               "Referer": "https://www.google.com/",
               "Cookie":""
            }
            cmd(headers)
        except Exception as e:
            logger.error("Exception: {} ".format(e))


#def valid_type(t):
#    """
#    引数のバリデーション
#    :param unicode t:
#    :rtype: int
#    """
#    try:
#        product_type = int(t)
#        if product_type in [1, 2, 3, 4]:
#            return product_type
#        raise argparse.ArgumentTypeError('Choices are 1, 2, 3, 4 but {0} are given'.format(product_type))
#    except ValueError:
#        raise argparse.ArgumentTypeError('Not a valid type: {}.'.format(t))

def cmd(headers):
    ymd = dt.today().strftime("%Y%m%d")
    price_total = ymd + ",";

    yyyy = dt.today().strftime("%Y")

    file_name = acl.get_amazon_coin_data_yyyy_csv_full_path(yyyy)
    #file_name = "/home/firenium/firenium.com/public_html/data/datavault/acoin/storage/data/amazon_coin_data_"+ yyyy +".csv";

    #500
    url = "https://www.amazon.co.jp/Amazon-500-Amazon%E3%82%B3%E3%82%A4%E3%83%B3/dp/B00KQVX53C"
    price = get_get_price(url, headers)
    price_total += price + ","
    time.sleep(11)

    #1000
    url = "https://www.amazon.co.jp/Amazon-500-Amazon%E3%82%B3%E3%82%A4%E3%83%B3/dp/B00KQVX7EY?th=1"
    price = get_get_price(url, headers)
    price_total += price + ","
    time.sleep(11)

    #2500
    url = "https://www.amazon.co.jp/Amazon-500-Amazon%E3%82%B3%E3%82%A4%E3%83%B3/dp/B00KQVX9J2?th=1"
    price = get_get_price(url, headers)
    price_total += price + ","
    time.sleep(11)

    #5000
    url = "https://www.amazon.co.jp/Amazon-500-Amazon%E3%82%B3%E3%82%A4%E3%83%B3/dp/B00KQVXBLS?th=1"
    price = get_get_price(url, headers)
    price_total += price + ","
    time.sleep(11)

    #10000
    url = "https://www.amazon.co.jp/Amazon-500-Amazon%E3%82%B3%E3%82%A4%E3%83%B3/dp/B00KQVXDW0?th=1"
    price = get_get_price(url, headers)
    price_total += price + ","
    time.sleep(11)

    #50000
    url = "https://www.amazon.co.jp/Amazon-500-Amazon%E3%82%B3%E3%82%A4%E3%83%B3/dp/B018GUTE1G?th=1"
    price = get_get_price(url, headers)
    price_total += price + "\n";

    #print(price_total)
    add_first_row(price_total,file_name)
    add_all_list_first_row(price_total)

def get_get_price(url,headers):
    #htmlの取得
    response = requests.get(url=url, headers=headers)#, cookies=cookie)
    html = response.content
    #BeautifulSoupで扱えるようにパースします
    soup = BeautifulSoup(html, "html.parser")
    ele_txt = soup.find(id="selectedProductPrice").get_text()
    # re.sub(正規表現パターン, 置換後文字列, 置換したい文字列)
    # \D : 10進数でない任意の文字。（全角数字等を含む）
    num = re.sub("\\D", "", ele_txt)
    print(num)
    return num

#ファイルの最初に追加
def add_first_row(price_total, file_name):

    if not os.path.isfile(file_name):
        with open(file_name, "w") as f:
            logger.info(file_name+"[新規作成]")

    with open(file_name) as f:
        l = f.readlines()

    l.insert(0, price_total)

    with open(file_name, mode='w') as f:
        f.writelines(l)

#一覧ファイルの最初に追加
def add_all_list_first_row(price_total):
    # 事前にファイルの内容を取得
    list_file_path = acl.get_amazon_coin_data_csv_full_path()
    #list_file_path = '/home/firenium/firenium.com/public_html/data/datavault/acoin/storage/data/amazon_coin_data.csv'
    if not os.path.isfile(list_file_path):
        with open(list_file_path, "w") as f:
            logger.info("amazon_coin_data.csv[新規作成]")

    with open(list_file_path) as f:
        l = f.readlines()

    l.insert(0, price_total)

    with open(list_file_path, mode='w') as f:
        f.writelines(l)
    #with open(list_file_path) as f:
    #    print(f.read())

#UAランダム
def get_random_ua():
    ua_array = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
    ];
    return random.choice(ua_array)

# ディレクトリ存在判定
def create_dir(target_dir):
    # 存在チェック
    if os.path.isdir(target_dir):
        print("ディレクトリが存在します")
    else:
        print("ディレクトリが存在しません")
    # ディレクトリがない場合、作成する
    if not os.path.exists(target_dir):
        print("ディレクトリを作成します")
        os.makedirs(target_dir)
    # 存在チェック
    if os.path.isdir(target_dir):
        print("ディレクトリが存在します")
    else:
        print("ディレクトリが存在しません")