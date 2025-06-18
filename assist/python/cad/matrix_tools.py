import numpy as np
def identity_matrix():
    """归一化矩阵"""
    return np.identity(4, dtype=float)  # 创建 4×4 整数型单位矩阵

def rotation_matrix(axis, theta):
    """生成绕指定轴旋转的4x4矩阵
    axis: 'x', 'y', 'z' 
    theta: 旋转角度（弧度）
    """
    c, s = np.cos(theta), np.sin(theta)
    if axis == 'x':  # 绕X轴
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ],dtype=float)
    elif axis == 'y':  # 绕Y轴
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ],dtype=float)
    elif axis == 'z':  # 绕Z轴
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ],dtype=float)
def translation_matrix(dx, dy, dz):
    """生成平移矩阵"""
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ],dtype=float)
def scaling_matrix(sx, sy, sz):
    """生成缩放矩阵"""
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ],dtype=float)

def org_matrix(local_point:list|tuple, scale:list|tuple, rotation)->np.array:
    # 创建变换矩阵
    R = rotation_matrix('z', rotation)  # 绕Z轴旋转90°
    T = translation_matrix(*local_point)   # 平移 (1,2,3)
    S = scaling_matrix(*scale)       # 缩放2倍

    # 组合变换：先缩放 → 再旋转 → 最后平移
    matrix = T @ R @ S
    return matrix
    
def point(matrix:np.array)->list[float]:
    return [float(matrix[i][3]) for i in range(3)]
def dest_point(_point:list|tuple, matrix):
    # 应用变换
    transformed_point = matrix @ translation_matrix(*_point)
    return point(transformed_point)

def scale(matrix:np.array)->list[float]:
    org_start=[0,0,0]
    org_end=[1,1,1]
    
    start=dest_point(org_start,matrix)
    end=dest_point(org_end,matrix)
    

    
    return [val1-val2 for val1,val2 in zip(end,start)]