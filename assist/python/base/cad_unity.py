import re
pos_pattern = r'-?\d+\.?\d*'  # 匹配整数、浮点数及负数[3,6](@ref)
def get_cmd_point(cmd_str)->tuple:
    numbers = re.findall(pos_pattern, cmd_str)
    if numbers:
        return tuple(map(float, numbers))


def get_cmd_points(data):
    formatted_lines =map(get_cmd_point,data.strip().split('\n'))
    return list(filter(lambda x: x, formatted_lines))

def create_cmd_point(point:list|tuple):
    str_data=[f'{x:.4f}' for x in point]
    return f"POINT {','.join(str_data)}\n"

def create_cmd_points(points:list[tuple|list]):
    points = get_cmd_points(points)
    if not points:
        return None
    cmd_str=map(create_cmd_point,points)
    
    return "".join(cmd_str)+"\n"

# 输入数据
input_data = """
控制点: X = 1519.7409, Y = 1578.0536, Z = 0.0000
X = 1755.4512, Y = 1490.6398, Z = 0.0000
X = 2170.0684, Y = 1336.8777, Z = 0.0000
X = 2486.1045, Y = 2207.6184, Z = 0.0000
X = 3187.5039, Y = 1380.4112, Z = 0.0000
X = 4027.7559, Y = 2278.6304, Z = 0.0000
X = 3221.6553, Y = 2300.5282, Z = 0.0000
X = 2694.2941, Y = 2314.8540, Z = 0.0000
"""

# 执行并输出
print(create_cmd_points(input_data))