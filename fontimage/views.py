# coding: utf-8
from django.shortcuts import render
from django.conf import settings
from django.views.generic import View
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import base64
import logging
from pprint import pprint
from . import fontimagelogic
from .forms import FontimageForm

global template_name
template_name = 'fontimage/index.html'

class FontimageIndexView(View):
    def get(self, req, *args, **kwargs):
        return render(req, template_name)

class FontimageCreateView(View):

    # コンストラクタの定義
    def __init__(self):
        self.generator_align = "default"
        self.params = {
            "build_string" : "",
            "img_alt" : "",
            "build_image" : "",
            "generator_align" : "",
            "data_uri" : "",
            "reg_color" : "",
            "form" : ""
        }

    def get(self, req, *args, **kwargs):
        if not req.GET.get("build_string"):
            return render(req, template_name, self.params)
        build_string = req.GET.get("build_string")

        self.params = fontimagelogic.FontimageLogic.param_create(self.params, build_string, self.generator_align)
        
        return render(req, template_name, self.params)

    def post(self, req, *args, **kwargs):
        
        form = FontimageForm(req.POST)
        if not form.is_valid():
            self.params['form'] = form
            return render(req, template_name, self.params)
        if not req.POST["build_string"]:
            return render(req, template_name, self.params)
        build_string = req.POST["build_string"]
         
        reg_color = '#000000'
        if req.POST["reg_color"]:
            #rgba_color = req.POST["rgba_color"].split(',')
            reg_color = req.POST["reg_color"]
        #print(reg_color)
        
        if "generator_align" in req.POST:
            self.generator_align = req.POST["generator_align"]
        
        self.params = fontimagelogic.FontimageLogic.param_create(self.params, build_string, self.generator_align,reg_color)
        return render(req, template_name, self.params)
    
    def exec_ajax(req,*args, **kwargs):
        """jQuery に対してレスポンスを返すメソッド"""
        if req.method == 'GET':  # GETの処理
            param1 = req.GET.get("param1")  # GETパラメータ1
            param2 = req.GET.get("param2")  # GETパラメータ2
            param3 = req.GET.get("param3")  # GETパラメータ3
            print(param1 + param2 + param3)
        fontimagelogic.FontimageLogic.get_slack_teams()
        return HttpResponse(f'こんにちは、unkoさん！')
#def create(req):
#    build_string = ""
#    generator_align = "default"
#
#    if req.method == 'GET':
#        if not req.GET.get("build_string"):
#            return render(req, 'fontimage/index.html', param)
#        build_string = req.GET.get("build_string")
#    elif req.method == 'POST':
#        if not req.POST["build_string"]:
#            return render(req, 'fontimage/index.html', param)
#        build_string = req.POST["build_string"]
#        # pprint(req.POST)
#        if "generator_align" in req.POST:
#            generator_align = req.POST["generator_align"]
#
#    try:
#        param["build_string"] = build_string
#        param["img_alt"] = build_string
#        param["generator_align"] = generator_align
#        # font_color = (0, 0, 0)
#        # im = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
#        # Image.new("RGB",(300,300),"")# Imageインスタンスを作る
#        #__font_path = "./flamevault/static/font/fgo_main_font.otf"
#        # fnt = ImageFont.truetype(__font_path, 30)  # ImageFontインスタンスを作る
#        # draw = ImageDraw.Draw(im)  # im上のImageDrawインスタンスを作る
#        # draw.text((0, 0), build_string, font=fnt)
#        __moji_create(build_string, generator_align)
#        # __pillow_char_offset(
#        #    0, 0, 128, 128, build_string, 150, __font_path)
#    except ValueError as err:
#        logger = logging.getLogger('CreateLogging')
#        fh = logging.FileHandler('logging.log')
#        logger.addHandler(fh)
#        logger.exception('Raise Exception: %s', err)
#    # except:
#    #    import traceback
#    #    traceback.print_exc()
#    return render(req, 'fontimage/index.html', param)


def __pillow_char_offset(x_pos: int, y_pos: int, x_end_pos: int, y_end_pos: int, char: str, init_font_size: int, fontfile_name: str):
    '''
    private method
    :param x_pos 文字を描画したい場所の[X]軸始点
    :param y_pos 文字を描画したい場所の[Y]軸始点
    :param x_end_pos 文字を描画したい場所の[X]軸終点
    :param y_end_pos 文字を描画したい場所の[Y]軸終点
    :param char 描画したい文字
    :param init_font_size フォントの初期値(最大サイズ)
    :param fontfile_name フォントファイル(otfやttf)のパス
    '''
    # ベースとなる画像の下地を作成する。複製した画像などをベースにする場合は Image.open で開く
    img = Image.new('L', (x_end_pos, y_end_pos), 'white')
    draw = ImageDraw.Draw(img)

    length = x_end_pos - x_pos
    height = y_end_pos - y_pos
    out_text_size = (length + 1, height + 1)
    font_size_offset = 0
    font = None

    # フォントの描画サイズが描画領域のサイズを下回るまでwhile
    while length < out_text_size[0] or height < out_text_size[1]:
        font = ImageFont.truetype(
            fontfile_name, init_font_size - font_size_offset)
        # draw.textsizeで描画時のサイズを取得
        out_text_size = draw.textsize(char, font=font)
        font_size_offset += 1

    draw.text((x_pos, y_pos), char, fill='#000', font=font)
    f = BytesIO()
    img.save(f, 'png')
    b64encoded = base64.b64encode(f.getvalue())
    param["data_uri"] = b64encoded.decode()


# def main(req):
#     if req.method == 'GET':
#         if not req.GET.get("build_string"):
#             return render(req, 'fontimage/index.html', param)
#         build_string = req.GET.get("build_string")
#     elif req.method == 'POST':
#         if not req.POST["build_string"]:
#             return render(req, 'fontimage/index.html', param)
#         build_string = req.POST["build_string"]

#     try:
#         __font_path = "./flamevault/static/font/fgo_main_font.otf"
#         fontsize = 30
#         ratio = 3
#         build_array = build_string.splitlines()
#         # 引き伸ばす前の大きさで画像を作成
#         truetype_font = ImageFont.truetype(__font_path, fontsize)
#         stb_w = 0
#         stb_h = 0
#         # width, height = truetype_font.getsize(build_string)
#         for row in build_array:
#             width, height = truetype_font.getsize(row)
#             if stb_w < width:
#                 stb_w = width
#             stb_h += height

#         W, H = (stb_w*ratio, stb_h*ratio)
#         img = Image.new('RGBA', (stb_w*ratio, stb_h*ratio), (255, 255, 255))
#         draw = ImageDraw.Draw(img)
#         # w, h = draw.textsize(build_string)
#         font = ImageFont.truetype(__font_path, fontsize*ratio)
#         # draw.text(((W-w)/2, (H-h)/2), build_string, fill='#000', font=font)
#         for row in build_array:
#             w, h = draw.textsize(row)
#             draw.text(((W-w)/2, (H-h)/2), row, fill='#000', font=font)
#         # 画像を縦に伸ばす
#         img2 = img.resize((256, 256))
#         f = BytesIO()
#         img2.save(f, 'png')
#         b64encoded = base64.b64encode(f.getvalue())
#         param["data_uri"] = b64encoded.decode()
#     except:
#         import traceback
#         traceback.print_exc()
#     return render(req, 'fontimage/index.html', param)


def __moji_create(build_string, align: str):
    try:
        __font_path = os.path.dirname(os.path.abspath(
            __file__)) + "/font/fgo_main_font.otf"
        pprint(__font_path)
        fontsize = 30
        ratio = 15
        build_array = build_string.splitlines()
        # 引き伸ばす前の大きさで画像を作成
        truetype_font = ImageFont.truetype(__font_path, fontsize)
        stb_w = 0
        stb_h = 0
        # width, height = truetype_font.getsize(build_string)
        for row in build_array:
            width, height = truetype_font.getsize(row)
            if stb_w < width:
                stb_w = width
            stb_h += height

        W, H = (stb_w*ratio, stb_h*ratio)
        img = Image.new('RGBA', (W, H), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(__font_path, fontsize*ratio)

        if align == 'left' or align == 'default':
            draw.text((0, 0), build_string, fill='#000',
                      font=font, spacing=10)
        else:
            (ww, hh) = (0, 0)
            for row in build_array:
                w, h = draw.textsize(row, font=font)
                if align == 'right':
                    ww = W-w
                if align == 'center':
                    ww = (W-w)/2

                draw.text((ww, hh), row,
                          fill='#000',  font=font, spacing=10)
                hh += h

        # 画像を縦に伸ばす
        img2 = img.resize((256, 256))
        f = BytesIO()
        img2.save(f, 'png')
        b64encoded = base64.b64encode(f.getvalue())
        param["data_uri"] = b64encoded.decode()
    except:
        import traceback
        traceback.print_exc()


# def __moji_create_naka(build_string, align: str):
#     try:
#         __font_path = "./flamevault/static/font/fgo_main_font.otf"
#         fontsize = 30
#         ratio = 15
#         build_array = build_string.splitlines()
#         # 引き伸ばす前の大きさで画像を作成
#         truetype_font = ImageFont.truetype(__font_path, fontsize)
#         stb_w = 0
#         stb_h = 0
#         # width, height = truetype_font.getsize(build_string)
#         for row in build_array:
#             width, height = truetype_font.getsize(row)
#             if stb_w < width:
#                 stb_w = width
#             stb_h += height

#         W, H = (stb_w*ratio, stb_h*ratio)
#         img = Image.new('RGBA', (W, H), (255, 255, 255))
#         draw = ImageDraw.Draw(img)
#         font = ImageFont.truetype(__font_path, fontsize*ratio)
#         #
#         (ww, hh) = (0, 0)
#         for row in build_array:
#             w, h = draw.textsize(row, font=font)
#             ww = (W-w)/2
#             draw.text((ww, hh), row,
#                       fill='#000',  font=font, spacing=10)
#             hh += h

#         # 画像を縦に伸ばす
#         img2 = img.resize((256, 256))
#         f = BytesIO()
#         img2.save(f, 'png')
#         b64encoded = base64.b64encode(f.getvalue())
#         param["data_uri"] = b64encoded.decode()
#     except:
#         import traceback
#         traceback.print_exc()


# def __moji_create_migi(build_string, align: str):
#     try:
#         __font_path = "./flamevault/static/font/fgo_main_font.otf"
#         fontsize = 30
#         ratio = 15
#         build_array = build_string.splitlines()
#         # 引き伸ばす前の大きさで画像を作成
#         truetype_font = ImageFont.truetype(__font_path, fontsize)
#         stb_w = 0
#         stb_h = 0

#         # width, height = truetype_font.getsize(build_string)
#         for row in build_array:
#             width, height = truetype_font.getsize(row)
#             if stb_w < width:
#                 stb_w = width
#             stb_h += height

#         W, H = (stb_w*ratio, stb_h*ratio)
#         img = Image.new('RGBA', (W, H), (255, 255, 255))
#         draw = ImageDraw.Draw(img)
#         font = ImageFont.truetype(__font_path, fontsize*ratio)
#         #
#         (ww, hh) = (0, 0)
#         for row in build_array:
#             w, h = draw.textsize(row, font=font)
#             ww = W-w
#             draw.text((ww, hh), row,
#                       fill='#000',  font=font,  spacing=10)
#             hh += h

#         # 画像を縦に伸ばす
#         img2 = img.resize((256, 256))
#         f = BytesIO()
#         img2.save(f, 'png')
#         b64encoded = base64.b64encode(f.getvalue())
#         param["data_uri"] = b64encoded.decode()
#     except:
#         import traceback
#         traceback.print_exc()
