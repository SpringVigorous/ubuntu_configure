import win32com.client
import math
from pyautocad import Autocad, APoint
from print_tools import print_info

class TextBoundingBoxExtractor:
    def __init__(self):
        pass

        
    def get_text_entities(self):
        """获取模型空间中的所有单行文本和多行文本"""
        text_entities = []
        for entity in self.doc.ModelSpace:
            if entity.ObjectName in ["AcDbText", "AcDbMText"]:
                text_entities.append(entity)
        return text_entities
    
    def rotate_point(self, point, angle, origin):
        """将点绕原点旋转指定角度"""
        x, y = point[0] - origin[0], point[1] - origin[1]
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        x_new = x * cos_a - y * sin_a
        y_new = x * sin_a + y * cos_a
        return (x_new + origin[0], y_new + origin[1])
    
    def get_single_text_bbox(self, text_entity):
        """获取单行文本的精确包围框"""
        try:
            # 获取基本属性
            position = text_entity.InsertionPoint
            height = text_entity.Height
            width_scale = text_entity.ScaleFactor
            rotation = text_entity.Rotation
            text_string = text_entity.TextString
            
            # 获取实际宽度（考虑字体）
            actual_width = text_entity.Width * width_scale
            
            # 计算包围框角点（未旋转）
            half_height = height / 2
            half_width = actual_width / 2
            
            # 根据对齐方式调整位置
            alignment = text_entity.Alignment
            if alignment != 0:  # 非左对齐
                justify_point = text_entity.TextAlignmentPoint
                x_j, y_j = justify_point[0], justify_point[1]
            else:
                x_j, y_j = position[0], position[1]
            
            # 基本角点（基于对齐点）
            points = [
                (x_j - half_width, y_j - half_height),  # 左下
                (x_j + half_width, y_j - half_height),  # 右下
                (x_j + half_width, y_j + half_height),  # 右上
                (x_j - half_width, y_j + half_height)   # 左上
            ]
            
            # 应用旋转
            rotated_points = [self.rotate_point(p, rotation, (x_j, y_j)) for p in points]
            
            return rotated_points
        except Exception as e:
            print_info(f"获取单行文本包围框失败: {str(e)}")
            return None
    
    def get_mtext_bbox(self, mtext_entity):
        """获取多行文本的精确包围框"""
        try:
            # 获取基本属性
            position = mtext_entity.InsertionPoint
            height = mtext_entity.Height
            actual_width = mtext_entity.Width
            rotation = mtext_entity.Rotation
            
            # 计算包围框尺寸（多行文本的Width属性直接表示宽度）
            half_height = height / 2
            half_width = actual_width / 2
            
            # 基本角点（未旋转）
            points = [
                (position[0] - half_width, position[1] - half_height),  # 左下
                (position[0] + half_width, position[1] - half_height),  # 右下
                (position[0] + half_width, position[1] + half_height),  # 右上
                (position[0] - half_width, position[1] + half_height)   # 左上
            ]
            
            # 应用旋转
            rotated_points = [self.rotate_point(p, rotation, position) for p in points]
            
            return rotated_points
        except Exception as e:
            print_info(f"获取多行文本包围框失败: {str(e)}")
            return None
    
    def calculate_minmax(self, points):
        """根据角点计算最小最大边界框"""
        if not points:
            return None
            
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        min_point = (min(x_coords), min(y_coords))
        max_point = (max(x_coords), max(y_coords))
        
        return (min_point, max_point)
    
    def get_text_bbox_info(self,entity):
        """获取所有文本实体的精确包围框"""
        if not entity:
            return None
        

        bbox_data = {
            "handle": entity.Handle,
            "text": entity.TextString,
            "type": entity.ObjectName,
            "position": entity.InsertionPoint,
            "height": entity.Height,
            "rotation": entity.Rotation
        }
        
        if entity.ObjectName == "AcDbText":
            # 单行文本处理
            corners = self.get_single_text_bbox(entity)
            bbox_data["width"] = entity.Width * entity.ScaleFactor
            bbox_data["alignment"] = entity.Alignment
        else:  # AcDbMText
            # 多行文本处理
            corners = self.get_mtext_bbox(entity)
            bbox_data["width"] = entity.Width
            bbox_data["alignment"] = None
        
        if corners:
            minmax = self.calculate_minmax(corners)
            bbox_data["corners"] = corners
            bbox_data["min_point"] = minmax[0]
            bbox_data["max_point"] = minmax[1]
            
            # 记录到日志
            print_info(f"文本处理成功: {entity.TextString[:30]}")
            print_info(f"类型: {entity.ObjectName}")
            print_info(f"位置: {entity.InsertionPoint}")
            print_info(f"旋转角度: {entity.Rotation}°")
            print_info(f"高度: {entity.Height}")
            print_info(f"宽度: {bbox_data['width']}")
            print_info(f"角点: {corners}")
            print_info(f"边界框: {minmax[0]} 到 {minmax[1]}")

        else:
            print_info(f"文本处理失败: {entity.Handle}")
    
        return bbox_data



# 使用示例
if __name__ == "__main__":
    extractor = TextBoundingBoxExtractor()
    
    # 获取所有文本包围框
    all_bboxes = extractor.get_text_bbox_info()
    
    # 打印统计信息
    extractor.logger.print_info(f"\n文本实体统计:")
    extractor.logger.print_info(f"共找到 {len(all_bboxes)} 个文本实体")
    
    # 在 AutoCAD 中可视化结果（可选）
    # extractor.visualize_bboxes()