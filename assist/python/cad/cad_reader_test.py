from pyautocad import Autocad
import math
import numpy as np
from matrix_tools import *
import win32com.client
from dwg_reader import DwgReader

file= open(r"F:\hg\BJY\drawing_recogniton_dispatch\dwg_to_image\dwgs\entity.log", "w", encoding="utf-8-sig")
def print_info(*args):
    file.write(f'{" ".join(map(str, args))}\n')
    

def transform_point(local_point, insert_point, scale, rotation):
    """将局部坐标转换为世界坐标"""
    # 缩放
    scaled = [local_point[i] * scale[i] for i in range(3)]
    # 旋转（绕Z轴）
    rot_matrix = [
        [math.cos(rotation), -math.sin(rotation), 0],
        [math.sin(rotation), math.cos(rotation), 0],
        [0, 0, 1]
    ]
    rotated = [
        scaled[0] * rot_matrix[0][0] + scaled[1] * rot_matrix[0][1],
        scaled[0] * rot_matrix[1][0] + scaled[1] * rot_matrix[1][1],
        scaled[2]
    ]
    # 平移
    return [insert_point[i] + rotated[i] for i in range(3)]

def print_line(entity, ids: list, matrix: np.array):
    
    start=dest_point( entity.StartPoint, matrix)
    end=dest_point( entity.EndPoint, matrix)
    
    """处理直线实体"""
    print_info("直线\n起点:", start, "\n终点:", end,"\nids:",ids,"\nscale:",scale(matrix),"\n")

def print_circle(entity, ids: list, matrix: np.array):
    """处理圆实体"""
    print_info("圆心:", entity.Center, "半径:", entity.Radius,"\nids:",ids,"\nscale:",scale(matrix),"\n")

def print_text(entity, ids: list, matrix: np.array):
    """处理单行文本实体"""
    print_info("文本\n位置:", entity.InsertionPoint, "内容:", entity.TextString,"\nids:",ids,"\nscale:",scale(matrix),"\n")

def print_mtext(entity, ids: list, matrix: np.array):
    """处理多行文本实体"""
    print_info("多行文本\n位置:", entity.InsertionPoint, "内容:", entity.TextString,"\nids:",ids,"\nscale:",scale(matrix),"\n")
    
def print_block(entity, ids: list, matrix: np.array):
    cur_matrix =org_matrix(entity.InsertionPoint, [entity.XScaleFactor, entity.YScaleFactor, entity.ZScaleFactor],entity.Rotation)
    matrix=matrix@cur_matrix
    
    block_def = doc.Blocks.Item(entity.Name)
    for sub_entity in block_def:
        print_entity(sub_entity,ids.copy(),matrix)
        
        
        
        
handler_map = {
    "AcDbLine": print_line,
    "AcDbCircle": print_circle,
    "AcDbText": print_text,
    "AcDbMText": print_mtext,
    "AcDbBlockReference": print_block,
    
}
def print_entity(entity, ids: list, matrix: np.array):
    """主分发函数：根据实体类型调用对应处理函数"""
    obj_type = entity.ObjectName
    
    ids.append(entity.Handle)
    # 使用字典映射替代if-elif链
    handler=handler_map.get(obj_type)
    
    if handler:
        handler(entity, ids, matrix)
    else:
        print_info(f"未处理的实体类型: {obj_type}","\nids:",ids,"\nscale:",scale(matrix),"\n\n")

def print_entities(msp):
    if not msp: return
    for entity in msp:
        ids=[]
        matrix=identity_matrix()
        print_entity(entity,ids,matrix)
                
if __name__ == "__main__":
    file_path = r"F:\hg\BJY\drawing_recogniton_dispatch\dwg_to_image\dwgs\1.dwg"
    doc = DwgReader.open_document(file_path)
    
    # msp = doc.ModelSpace
    
    # print_info("--- 模型空间实体 ---")
    
    # print_entities(msp)
    # 2. 打印图纸空间实体类型（PaperSpace）
    print_info("--- 图纸空间实体 ---")
    layouts = doc.Layouts
    for layout in layouts:
        # 获取布局对应的图纸空间Block[7,8](@ref)
        print_info(f"布局名称: {layout.Name}")
        block = layout.Block
        print_entities(block)

    DwgReader.close_current_document()

    DwgReader.shutdown()
    
    
    file.close()
    
