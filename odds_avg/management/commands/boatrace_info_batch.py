from django.core.management.base import BaseCommand
import sys
import io
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import argparse
import socket
import time
from logging import basicConfig, getLogger, DEBUG
from datetime import datetime
from ...logic import boatracebatch
from ...logic import scrapingbatch
from django.conf import settings
class Command(BaseCommand):

    # ネットワーク設定の初期化
    origGetAddrInfo = socket.getaddrinfo
    def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
        return Command.origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)
    
    # [python manage.py help sampleBatch]で表示されるメッセージ
    help = 'これはテスト用のコマンドバッチです'
    # これはメインのファイルにのみ書く
    basicConfig(level=DEBUG)

    def add_arguments(self, parser):
        # コマンドライン引数を指定
        parser.add_argument('-d', action='store', dest='day_value', help='時間の形式はyyyymmddで入力してください',required=False, type=valid_day_type)

    def handle(self, *args, **options):
        start = time.time()
        logger = getLogger(__name__)
        socket.getaddrinfo = Command.getAddrInfoWrapper
        try:
            logger.debug('バッチが動きました： {}'.format(options['day_value']))
            bbu = boatracebatch.BoatRaceBatchLogic()
            sbl = scrapingbatch.ScrapingBatchLogic()
            
            day = datetime.today().strftime("%Y%m%d")
            if options['day_value'] is not None:
                day = options['day_value']
            sbl.create_race_info_places(day)
            bbu.create_race_info_places_bk()
            sbl.create_race_deadline_time(day)
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.debug(e)
        finally:
            elapsed_time = time.time() - start
            logger.debug ("elapsed_time:{0}".format(elapsed_time) + "[sec]")


def valid_day_type(d):
    """
    引数のバリデーション
    :param unicode t:
    :rtype: int
    """
    if len(d) > 8:
        raise argparse.ArgumentTypeError('Over length {0}'.format(d))
    try:
        tmp = datetime.strptime(d, "%Y%m%d")
        return d
    except ValueError:
        #不正な日付の場合、ValueErrorが発生する
        raise argparse.ArgumentTypeError('日付の妥当性がありません {0}'.format(d))