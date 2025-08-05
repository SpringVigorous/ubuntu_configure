import re

def extract_file_rotations(log_text: str) -> list:
    """
    从日志文本中提取文件路径和旋转值
    Args:
        log_text: 包含文件路径和旋转值的日志文本
    Returns:
        list: 元组列表 [(文件路径, 旋转值)]，旋转值为整数（不存在时返回0）
    """
    # 定义匹配文件路径和旋转值的正则表达式
    pattern = r"""
        (?:详情[:：]\s*)      # 匹配"详情："或"详情："
        ([a-zA-Z]:[/][^,\s]+)  # 匹配Windows文件路径（含盘符）[7](@ref)
        (?:,|\s*,\s*)        # 匹配逗号分隔符
        (?:旋转值[:：]\s*(\d+))? # 匹配旋转值（可能不存在）[6](@ref)
    """
    
    results = []
    # 逐行处理日志[5](@ref)
    for line in log_text.split('\n'):
        # 使用正则匹配（忽略大小写和空白）
        match = re.search(pattern, line, re.VERBOSE | re.IGNORECASE)
        if not match:
            continue
            
        file_path = match.group(1)  # 提取文件路径
        rotation = match.group(2)   # 提取旋转值
        
        # 处理旋转值不存在的情况
        rotation_value = int(rotation) if rotation else 0
        results.append((file_path, rotation_value))
    
    return results

# 测试数据
log_data = """
2025-08-04 23:33:11,022-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_16201502010f7b.mp4 -> E:/video/20250804/video_20250804_162015.mp4
2025-08-04 23:33:11,023-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_162015.mp4,旋转值：180
2025-08-04 23:33:12,915-ERROR-Thread ID: 12648-NAME: MainThread-【移动文件】-【失败】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_1626390767f8e5.mp4 -> E:/video/20250804/video_20250804_162639.mp4,C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_1626390767f8e5.mp4 权限不够
2025-08-04 23:33:12,917-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_162639.mp4,旋转值：90
2025-08-04 23:33:13,753-TRACE-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【忽略】详情：E:/video/20250804/video_20250804_162658.mp4,旋转值：0,直接返回
2025-08-04 23:33:22,889-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_163529103cafe6.mp4 -> E:/video/20250804/video_20250804_163529.mp4
2025-08-04 23:33:22,891-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_163529.mp4,旋转值：90
2025-08-04 23:33:23,777-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_163550a1febdaa.mp4 -> E:/video/20250804/video_20250804_163550.mp4
2025-08-04 23:33:23,779-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_163550.mp4,旋转值：90
2025-08-04 23:33:24,613-TRACE-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【忽略】详情：E:/video/20250804/video_20250804_163638.mp4,旋转值：0,直接返回
2025-08-04 23:33:25,679-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_163808272f79d1.mp4 -> E:/video/20250804/video_20250804_163808.mp4
2025-08-04 23:33:25,680-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_163808.mp4,旋转值：180
2025-08-04 23:33:27,628-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_163826e844025e.mp4 -> E:/video/20250804/video_20250804_163826.mp4
2025-08-04 23:33:27,629-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_163826.mp4,旋转值：90
2025-08-04 23:33:29,787-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_1641509ecb23a3.mp4 -> E:/video/20250804/video_20250804_164150.mp4
2025-08-04 23:33:29,788-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_164150.mp4,旋转值：90
2025-08-04 23:33:31,930-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_164536105d0dc3.mp4 -> E:/video/20250804/video_20250804_164536.mp4
2025-08-04 23:33:31,931-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_164536.mp4,旋转值：90
2025-08-04 23:33:33,913-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_164807b8109280.mp4 -> E:/video/20250804/video_20250804_164807.mp4
2025-08-04 23:33:33,914-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_164807.mp4,旋转值：90
2025-08-04 23:33:36,001-DEBUG-Thread ID: 12648-NAME: MainThread-【移动文件】-【成功】详情：C:/Users/Administrator/AppData/Local/Temp/video_cache/video_20250804_165041fbe20ad2.mp4 -> E:/video/20250804/video_20250804_165041.mp4
2025-08-04 23:33:36,002-INFO-Thread ID: 12648-NAME: MainThread-【清除视频元数据-旋转值】-【成功】详情：E:/video/20250804/video_20250804_165041.mp4,旋转值：90
"""

# 执行提取
rotations = extract_file_rotations(log_data)

# 打印结果
for i, (path, rot) in enumerate(rotations, 1):
    print(f"{i}. 文件路径: {path}\n   旋转值: {rot}°")