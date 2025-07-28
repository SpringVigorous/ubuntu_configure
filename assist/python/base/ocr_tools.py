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
from com_log import logger_helper,UpdateTimeType
def has_non_ascii(s):
    # 检查所有字符的ASCII码是否都在0-127之间
    return not all(ord(c) < 128 for c in s)

def crop_image_with_offsets(image, crop_height=1000, overlap=100):
    """
    裁剪图片为子图并记录每个子图的偏移量
    优化点：
    1. 先判断图片高度是否小于等于裁剪高度，若满足则不拆分
    2. 第一个子图不设置重叠，从第二个子图开始应用重叠
    :param image: 原图
    :param crop_height: 每个子图的高度
    :param overlap: 子图间的重叠像素数（从第二个子图开始生效）
    :return: 子图列表和对应的偏移量列表 (y方向偏移)
    """
    h, w = image.shape[:2]
    
    # 新增：如果图片高度小于等于裁剪高度，直接返回原图，不拆分
    if h <= crop_height:
        return [image], [0]  # 子图列表只包含原图，偏移量为0
    
    sub_images = []
    offsets = []  # 记录每个子图在原图中的y坐标偏移
    start_y = 0
    sub_image_index = 0  # 用于标记是否为第一个子图
    
    while start_y < h:
        # 计算当前子图的结束y坐标
        end_y = start_y + crop_height
        # 确保最后一个子图不会超出原图范围
        if end_y > h:
            end_y = h
        
        # 裁剪子图
        sub_img = image[start_y:end_y, :, :]
        sub_images.append(sub_img)
        offsets.append(start_y)
        
        # 计算下一个子图的起始位置
        if sub_image_index == 0:
            # 第一个子图之后，直接从end_y开始，不考虑重叠
            next_start_y = end_y
        else:
            # 从第二个子图开始，应用重叠
            next_start_y = end_y - overlap
        
        # 防止无限循环（当剩余高度小于重叠区域时）
        if next_start_y >= h or next_start_y <= start_y:
            break
            
        start_y = next_start_y
        sub_image_index += 1
    
    return sub_images, offsets

# def adjust_bbox_coordinates(ocr_results, offset_y):
#     """
#     调整子图的OCR结果坐标到原图坐标系
#     :param ocr_results: 子图的OCR识别结果
#     :param offset_y: 子图在原图中的y方向偏移量
#     :return: 校正后的OCR结果
#     """
#     adjusted_results = []
#     for line in ocr_results:
#         # 每个line是一个包含[检测框, [文本, 置信度]]的列表
#         bbox, text_info = line
#         adjusted_bbox = []
#         # 调整检测框的y坐标（每个点都是(x, y)）
#         for (x, y) in bbox:
#             adjusted_bbox.append((x, y + offset_y))
#         adjusted_results.append([adjusted_bbox, text_info])
#         line[0]=adjusted_bbox
#     return adjusted_results

def adjust_bbox_coordinates(ocr_results, offset_y):
    """
    调整子图的OCR结果坐标到原图坐标系
    :param ocr_results: 子图的OCR识别结果
    :param offset_y: 子图在原图中的y方向偏移量
    :return: 校正后的OCR结果
    """
    for  i in range(len(ocr_results)):
        line=ocr_results[i]
        # 每个line是一个包含[检测框, [文本, 置信度]]的列表
        bbox, _ = line
        # print(bbox)
        
        # 调整检测框的y坐标（每个点都是(x, y)）
        for j in range(len(bbox)):
            bbox[j][1] += offset_y
        
        
        # print(bbox)

        
    return ocr_results




def ocr_large_image(ocr_obj,image_path,  crop_height=1000, overlap=100):
    """
    处理大图片的OCR识别，包括裁剪、识别、坐标校正和结果合并
    :param image_path: 图片路径
    :param ocr: PaddleOCR实例
    :param crop_height: 子图高度
    :param overlap: 子图重叠像素
    :return: 合并后的OCR结果（坐标对应原图）
    """
    
            
    # 存储所有校正后的结果
    all_results = []
    image=None
    # 读取原图
    cache_path=image_path
    if has_non_ascii(image_path):
        
        cur_path:Path=Path(image_path)
        name=cur_path.name if not has_non_ascii(cur_path.stem) else f"temp_{cur_path.suffix}"
        cache_path =os.path.join(tempfile.gettempdir(),"ocr_picture",name)
        import shutil
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        shutil.copy2(image_path, cache_path)

    try:
        image = cv2.imread(cache_path)
        if image is None:
            return all_results
    except Exception as e:
        print(e)
    
    finally:
        if cache_path!=image_path:
            os.remove(cache_path)
    
    # 裁剪为子图并获取偏移量
    sub_images, offsets = crop_image_with_offsets(image, crop_height, overlap)
    
    
    # 逐个处理子图
    for i, (sub_img, offset_y) in enumerate(zip(sub_images, offsets)):
        print(f"处理子图 {i+1}/{len(sub_images)}...")
        # 识别子图（cls=True表示使用方向分类器）
        # result = ocr.ocr(sub_img, cls=True)
        result = ocr_obj(sub_img, cls=True)
        if result is None:
            continue
        
        # 校正坐标并添加到总结果
        dest=adjust_bbox_coordinates(result[0], offset_y)
        #重叠部分，需要减去
        
        if all_results:
            min_y=offset_y
            max_y=offset_y+overlap

            def is_inner(result):
                
                box,_=result
                # 计算矩形边界

                y_coords = [p[1] for p in box]
                cur_min_y,cur_max_y= min(y_coords),max(y_coords)
                
                
                return not(cur_min_y>=min_y and cur_max_y<=max_y)

            dest=list(filter(is_inner, dest))
            
            
            pass
        
        
        all_results.extend(dest)
    
    return all_results


class OCRProcessor:
    """
    PaddleOCR 处理类，封装OCR识别和结果可视化功能
    
    示例用法:
        processor = PaddleOCRProcessor(lang='ch')
        result_image = processor.process_image(
            img_path="input.jpg",
            output_path="output.png",
            font_path="simhei.ttf"
        )
    """

    def __init__(self, lang: str = 'ch', **ocr_kwargs):
        """
        初始化OCR处理器
        
        :param lang: 识别语言，默认为中文('ch')
        :param ocr_kwargs: 传递给PaddleOCR的其他参数
        """
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang,use_mp=True, **ocr_kwargs)
        self.default_font = 'simhei.ttf'
        self.logger = logger_helper("文字识别")
        

    def recognize_text(self, img_path: str) -> Tuple[List, List, List]:
        """
        执行OCR识别
        
        :param img_path: 图片路径
        :return: (boxes, texts, scores) 三元组
        """
        
        self.logger.update_target(detail=f"{img_path}")
        self.logger.update_time(UpdateTimeType.ALL)
        
        # self.logger.trace("开始")
        
        result=None
        try:
            result = ocr_large_image(self.ocr.ocr,img_path,1980,200)
            # self.logger.trace("完成",update_time_type=UpdateTimeType.STEP)
        except Exception as e:
            print(f"失败: {str(e)}")
            pass
        finally:
            self.logger.info("完成",update_time_type=UpdateTimeType.ALL)    
        
        if not result:
            return [], [], []
            
        # result = result[0]  # 获取第一页结果
        
        if not result:
            return [], [], []
            
        
        boxes = [line[0] for line in result if line]
        texts = [line[1][0] for line in result if line]
        scores = [line[1][1] for line in result if line]
        return boxes, texts, scores

    def visualize_results(
        self,
        image: Image.Image,
        boxes: List,
        texts: List[str],
        scores: List[float],
        font_path: Optional[str] = None
    ) -> Image.Image:
        """
        可视化OCR结果
        
        :param image: PIL Image对象
        :param boxes: 边界框坐标
        :param texts: 识别文本列表
        :param scores: 置信度分数列表
        :param font_path: 字体路径，默认为系统simhei字体
        :return: 标注后的Image对象
        """
        draw = ImageDraw.Draw(image)
        
        # 设置字体
        font_path = font_path or self._find_system_font()
        try:
            font = ImageFont.truetype(font_path, size=25)
        except:
            font = ImageFont.load_default()
            self._log_warning(f"字体 {font_path} 加载失败，使用默认字体")

        for i, box in enumerate(boxes):
            # 计算矩形边界
            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]
            x0, y0 = min(x_coords), min(y_coords)
            x1, y1 = max(x_coords), max(y_coords)

            # 绘制识别框
            # draw.rectangle([x0, y0, x1, y1], outline='red', width=2)
            draw.polygon([tuple(p) for p in box], outline="red", width=2)

            # 准备文本
            text = f"{i}:{texts[i]} ({scores[i]:.2f})"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # 计算文本位置
            text_y = y0 - text_height - 5
            if text_y < 0:  # 如果超出上边界
                text_y = y1 + 5

            # 绘制文本背景和文字
            text_rect = [x0, text_y, x0 + text_width, text_y + text_height]
            # draw.rectangle(text_rect, fill='black')
            draw.polygon([tuple([x0,text_y]),tuple([x0+text_width,text_y]),tuple([x0+text_width,text_y+ text_height]),tuple([x0,text_y+ text_height])],  outline="white", width=2)
            draw.text((x0, text_y), text, font=font, fill='red')

        return image

    def process_image(
        self,
        img_path: str,
        output_path: Optional[str] = None,
        font_path: Optional[str] = None,
        save_result: bool = True
    ) -> tuple[Image.Image,tuple|list]:
        """
        完整处理流程：识别+可视化
        
        :param img_path: 输入图片路径
        :param output_path: 输出图片路径
        :param font_path: 字体路径
        :param save_result: 是否保存结果
        :return: 标注后的Image对象
        """
        
        result_image,ocr_results=[None]*2
        try:
            
            # OCR识别
            ocr_results = self.recognize_text(img_path)
            boxes, texts, scores=ocr_results
            
            # 打开原图
            image = Image.open(img_path).convert("RGB")
            
            # 可视化结果
            result_image = self.visualize_results(image, boxes, texts, scores, font_path)
            
            # 保存结果
            if save_result:
                output_path = output_path or os.path.join(
                    os.path.dirname(img_path),
                    f"result_{os.path.basename(img_path)}"
                )
                result_image.save(output_path)
                print(f"结果已保存至: {output_path}")
        except Exception as e:
            print(f"处理图片时出错: {e}")
            pass
        
        
        
        finally:
        
            return result_image,ocr_results

    def _find_system_font(self) -> str:
        """查找系统字体"""
        # Windows字体路径
        if os.name == 'nt':
            font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
            hei_font = os.path.join(font_dir, 'simhei.ttf')
            if os.path.exists(hei_font):
                return hei_font
        return self.default_font

    def _log_warning(self, message: str):
        """打印警告信息"""
        print(f"[警告] {message}")

# 使用示例
if __name__ == "__main__":
    # 初始化处理器
    processor = OCRProcessor(lang='ch')
    
    
    
    
    # 处理单张图片
    processor.process_image(
        img_path=r"F:\worm_practice\taobao\图片\2.jpg",
        output_path=r"F:\worm_practice\taobao\图片\2-识别.jpg",
        font_path='simhei.ttf'
    )