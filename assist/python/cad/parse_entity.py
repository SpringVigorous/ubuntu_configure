import win32com.client
from pyautocad import Autocad, APoint
from matrix_tools import *
from print_tools import print_info

def parse_viewport(entity, ids: list, matrix: np.array):
    if entity.ObjectName != "AcDbViewport":
        return
   
    # 解析视口

    print_info(f"\n解析视口 {entity.Handle}")
    
    # 1. 中心点（图纸空间）
    center = APoint(entity.Center)
    print_info(f"中心点: ({center.x}, {center.y})")
    
    # 2. 尺寸（图纸空间）
    width = entity.Width
    height = entity.Height
    print_info(f"尺寸: {width} x {height}")
    
    # 3. 缩放比例
    scale = entity.CustomScale
    print_info(f"缩放比例: 1:{1/scale}" if scale != 0 else "缩放比例: 无")
    
    # 4. 计算变换矩阵（模型空间 -> 图纸空间视口）
    matrix = get_transform_matrix(entity, width, height, scale)
    print_info("变换矩阵:")
    for row in matrix:
        print_info(row)

def get_transform_matrix(vp, width, height, scale):
    """计算模型空间到图纸空间视口的变换矩阵"""
    # 视口图纸空间角点
    center = vp.Center
    x_min = center[0] - width / 2
    y_min = center[1] - height / 2
    
    # 获取视口视图方向（模型空间）
    direction = vp.Direction
    target = vp.Target

    print_info(f"视口方向：{direction}")
    print_info(f"视口目标：{target}")
    # 基础变换：缩放和平移到视口区域
    # 注意：AutoCAD 视口变换包含旋转/倾斜，需额外计算方向向量
    T = [
        [scale, 0, 0, x_min],
        [0, scale, 0, y_min],
        [0, 0, scale, 0],
        [0, 0, 0, 1]
    ]
    
    # 添加视图方向修正（简化版，实际需计算方向矩阵）
    # 此处仅为示例，完整3D变换需叉乘计算坐标系
    return T

if __name__ == "__main__":
    parse_viewport()