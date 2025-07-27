import easyocr
from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
import os
import numpy as np
# from com_log import logger_helper,UpdateTimeType
import cv2
import tempfile
from pathlib import Path

class ImageHelper:
    
    
    default_font = 'simhei.ttf'
    def __init__(self):
        pass
        
    @staticmethod
    def open_draw(image_path,mode="RGB") -> ImageDraw:
        # 打开原图->先转指定模式
        image = Image.open(image_path).convert(mode)
        #再转正常彩色模式
        if mode != "RGB":
            image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        return image,draw
        
    @staticmethod
    def save_draw(draw:ImageDraw, image_path):
        draw.save(image_path)
    
    @staticmethod
    def create_font(font_path: Optional[str] = None):
        font=None
        # 设置字体
        font_path = font_path or ImageHelper._find_system_font()
        try:
            font = ImageFont.truetype(font_path, size=25)
        except:
            font = ImageFont.load_default()
        finally:
            return font
       
    @staticmethod
    def box_pos(box):   
        # 计算矩形边界
        x_coords = [p[0] for p in box]
        y_coords = [p[1] for p in box]
        x0, y0 = min(x_coords), min(y_coords)
        x1, y1 = max(x_coords), max(y_coords)
        
        return (x0,y0),(x1,y1)
    #返回包围框的左顶、右底坐标
    @staticmethod
    def draw_box(
        image_draw:ImageDraw,
        box: List,
        color: str = 'red')->tuple :
        
        # 计算矩形边界
        pos=ImageHelper.box_pos(box)


        # 绘制识别框
        # draw.rectangle([x0, y0, x1, y1], outline='red', width=2)
        image_draw.polygon([tuple(p) for p in box], outline=color, width=2)
        
        return pos
    @staticmethod
    def draw_text(draw, pos:tuple|list, text, font, color='red'):
        (x0,y0),(x1,y1)=pos
        # 准备文本

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_height = text_bbox[3] - text_bbox[1]

        # 计算文本位置
        text_y = y0 - text_height - 5
        if text_y < 0:  # 如果超出上边界
            text_y = y1 + 5
        draw.text((x0, text_y), text, font=font, fill=color)
    

    @staticmethod
    def draw(src_img_path,output_img_path,boxes,dest_index,font_path=None,box_color='red',text_color='red'):
        
        font=ImageHelper.create_font(font_path)
        img,img_draw=ImageHelper.open_draw(src_img_path,mode="L")
        sort_dict={}
        
        for index,texts in dest_index.items():
            
            item=(index,texts)
            
            i=index[0]
            if sort_dict.get(i) is None:
                sort_dict[i]=[item]
            else:
                sort_dict[i].append(item)
        
        
        for _index,item in sort_dict.items():
            box=[]
            whole_text=[]
            for index,texts in item:
                for i in index:
                    if i >= len(boxes):
                        continue
                    box.extend(boxes[i])
                whole_text.extend(texts)
                    
            text=f"【{'】【'.join(whole_text)}】"
            pos=ImageHelper.box_pos(box)
            (x0,y0),(x1,y1)=pos
            
            box=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
            ImageHelper.draw_box(img_draw,box,color=box_color)
            ImageHelper.draw_text(img_draw,pos,text,font=font,color=text_color)
            
        img.save(output_img_path)
        
    
    @staticmethod
    def _find_system_font() -> str:
        """查找系统字体"""
        # Windows字体路径
        if os.name == 'nt':
            font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
            hei_font = os.path.join(font_dir, 'simhei.ttf')
            if os.path.exists(hei_font):
                return hei_font
        return ImageHelper.default_font
    