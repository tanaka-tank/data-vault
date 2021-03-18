from django.core.management.base import BaseCommand
import sys
import io
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import argparse
import socket
import time
from logging import basicConfig, getLogger, ERROR
from datetime import datetime
from ...utils import boatrace
from ...logic import boatracebatch
from ...conf import const


class Command(BaseCommand):

    # ネットワーク設定の初期化
    origGetAddrInfo = socket.getaddrinfo
    def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
        return Command.origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)
    
    # [python manage.py help sampleBatch]で表示されるメッセージ
    help = 'これはテスト用のコマンドバッチです'
    # これはメインのファイルにのみ書く
    basicConfig(level=ERROR)

    def add_arguments(self, parser):
        # コマンドライン引数を指定
        parser.add_argument('-p', action='store', dest='place_value', help='【必須】ashiya,omura,tokuyama,allから選んでください',required=True, type=valid_place_type)
        parser.add_argument('-b', action='store', dest='bet_type', help='【必須】2tan,2puku,3tan,3puku,9 から選んでください',required=True, type=valid_bet_type)
        parser.add_argument('-r', action='store', dest='race_no')

    def handle(self, *args, **options):
        start = time.time()

        socket.getaddrinfo = Command.getAddrInfoWrapper
        #logger = getLogger(__name__)
        logger = getLogger("file")
        
        res_comment = {}
        try:
            logger.debug('バッチが動きました：place_value-> {} bet_type-> {}'.format(options['place_value'],options['bet_type']))

            place = options['place_value']
            bet_type = options['bet_type']
            race_no = options['race_no']
            #day = datetime.today().strftime("%Y%m%d")
            
            bbu = boatracebatch.BoatRaceBatchLogic()
            res_comment = bbu.create_odds_file_places(place,bet_type,race_no)
        except Exception as e:
            #import traceback
            #traceback.print_exc()
            logger.error(e)
        finally:
            elapsed_time = time.time() - start
            logger.debug("elapsed_time:{0}".format(elapsed_time) + "[sec]")
            logger.debug(res_comment)
            #import json
            #logger.debug(json.dumps(res_comment))


def valid_place_type(p):
    """
    引数のバリデーション
    :param unicode p:
    :rtype: str
    """
    try:
        if boatrace.BoatRaceUtils.is_effect_place(p):
            return p
        raise argparse.ArgumentTypeError('Choices are ashiya, omura, tokuyama but {0} are given'.format(p))
    except ValueError:
        raise argparse.ArgumentTypeError('Not a valid type: {}.'.format(p))

def valid_bet_type(b):
    """
    引数のバリデーション
    :param unicode b:
    :rtype: str
    """
    try:
        if b == const.BET_2TAN or b == const.BET_3TAN or b == const.BET_2PUKU or b == const.BET_3PUKU or b == const.BET_ALL:
            return b
        raise argparse.ArgumentTypeError('Choices are 2tan,2puku,3tan,3puku,9 but {0} are given'.format(b))
    except ValueError:
        raise argparse.ArgumentTypeError('Not a valid type: {}.'.format(b))
    