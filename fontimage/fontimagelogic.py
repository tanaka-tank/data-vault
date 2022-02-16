import os
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging
from bs4 import BeautifulSoup
import lxml.html
import requests
from pprint import pprint

class FontimageLogic:

    def __init__(self, value=''):
        self.value = value

    def param_create(param,build_string, generator_align,reg_color):
        try:
            param["build_string"] = build_string
            param["img_alt"] = build_string
            param["generator_align"] = generator_align
            param["reg_color"] = reg_color
            param["data_uri"] = "data:image/png;base64," + FontimageLogic.__moji_create(build_string, generator_align, reg_color)
        except ValueError as err:
            logger = logging.getLogger('CreateLogging')
            fh = logging.FileHandler('logging.log')
            logger.addHandler(fh)
            logger.exception('Raise Exception: %s', err)
        return param
    
    def get_slack_teams():
        try:
            # ログインページのURLから、BeautifulSoupオブジェクト作成
            print("--------------------")
            
            url = "https://api.slack.com/customize/emoji"
            session = requests.session()
            print("--------------------")
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
            response = session.get(url,verify=False,headers = headers)
            print("--------------------")
            
            bs = BeautifulSoup(response.text, 'html.parser')
            
            # クッキーとトークンを取得
            #authenticity = bs.find(attrs={'name':'crumb'}).get('value')
            #cookie = response.cookies
            
            # ログイン情報
            #info = {
            #    "_token": authenticity,
            #    "email": "メールアドレス",
            #    "password": "ログインパスワード",
            #}
            
            # URLを叩き、htmlを表示
            #res = session.post(url, data=info, cookies=cookie)
            #print(bs)
            print("--------------------")
        except ValueError as err:
            logger = logging.getLogger('CreateLogging')
            fh = logging.FileHandler('logging.log')
            logger.addHandler(fh)
            logger.exception('Raise Exception: %s', err)
        return
    
    def __moji_create(build_string, align: str, reg_color):
        try:
            __font_path = os.path.dirname(os.path.abspath(__file__)) + "/font/fgo_main_font.otf"
            #pprint(__font_path)
            __fontsize = 30
            __ratio = 15

            build_string = build_string.rstrip()
            build_array = build_string.splitlines()
            # 引き伸ばす前の大きさで画像を作成
            truetype_font = ImageFont.truetype(__font_path, __fontsize)
            total_w = 0
            total_h = 0
            __stb_zero_h = 0

            for row in build_array:
                width, height = truetype_font.getsize(row)
                if total_w < width:
                    total_w = width
                if height != 0:
                    __stb_zero_h = height
                if row == '':
                    total_h += __stb_zero_h
                if row != '':
                    total_h += height
    
            W, H = (total_w * __ratio, total_h * __ratio)
            
            img  = Image.new('RGBA', (W, H), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(__font_path, __fontsize * __ratio)

            (width, height), (offset_x, offset_y) = font.font.getsize(build_string)

            canvas_size = (256,256)
            text_width, text_height = draw.textsize(build_string,font=font)
            
            text_top_left = (0,0-(offset_y//2))
            if FontimageLogic.__is_japanese(build_string):
                text_top_left = (0,0)
            if len(build_array) == 1 and not FontimageLogic.__is_japanese(build_string):
                text_top_left = ((W-text_width)//2,(canvas_size[1]-text_height)//2)
            
            if align == 'left' or align == 'default':
                draw.text(
                    text_top_left,
                    build_string,
                    fill=reg_color,
                    font=font,
                    spacing=10)
            else:
                (ww, hh) = (0, 0-(offset_y//2))
                __stb_zero_h = 0
                for row in build_array:
                    w, h = draw.textsize(row, font=font)
                    if align == 'right':
                        ww = W-w
                    if align == 'center':
                        ww = (W-w)//2

                    draw.text((ww, hh), row, fill=reg_color,  font=font, spacing=10)
                    if row == '':
                        draw.text((ww, hh), "", fill=reg_color,  font=font, spacing=10)
                    if h != 0:
                        __stb_zero_h = h
                    if row == '':
                        hh += __stb_zero_h
                    if row != '':
                        hh += h
    
            # 画像を縦に伸ばす
            img2 = img.resize(canvas_size)
            f = BytesIO()
            img2.save(f, 'png')

            b64encoded = base64.b64encode(f.getvalue())
            #param["data_uri"] = b64encoded.decode()
            return b64encoded.decode()
        except:
            import traceback
            traceback.print_exc()
    
    def __is_japanese(string):
        import unicodedata
        string = ''.join(string.splitlines())
        print(string)
        for ch in string:
            name = unicodedata.name(ch) 
            if "CJK UNIFIED" in name \
            or "HIRAGANA" in name \
            or "KATAKANA" in name:
                return True
        return False