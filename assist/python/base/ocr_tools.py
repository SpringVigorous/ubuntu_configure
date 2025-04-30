import easyocr
from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
import os

# from com_log import logger_helper,UpdateTimeType

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
        # self.logger = logger_helper("文字识别")
        

    def recognize_text(self, img_path: str) -> Tuple[List, List, List]:
        """
        执行OCR识别
        
        :param img_path: 图片路径
        :return: (boxes, texts, scores) 三元组
        """
        
        # self.logger.update_target(detail="img_path")
        # self.logger.update_time(UpdateTimeType.ALL)
        
        # self.logger.trace("开始")
        
        result=None
        try:
            result = self.ocr.ocr(img_path)
            # self.logger.trace("完成",update_time_type=UpdateTimeType.STEP)
        except:
            pass
            
        if not result:
            return [], [], []
            
        result = result[0]  # 获取第一页结果
        
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
    ) -> tuple[Image.Image,list[str]]:
        """
        完整处理流程：识别+可视化
        
        :param img_path: 输入图片路径
        :param output_path: 输出图片路径
        :param font_path: 字体路径
        :param save_result: 是否保存结果
        :return: 标注后的Image对象
        """
        # OCR识别
        boxes, texts, scores = self.recognize_text(img_path)
        
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
        
        return result_image,texts

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