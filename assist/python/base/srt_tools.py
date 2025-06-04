def generate_srt(subtitles, output_file, time_unit="ms"):
    """
    将时间序列和字幕文本转换为SRT格式
    :param subtitles: 列表格式，每个元素为元组 (start, end, text)
    :param output_file: 输出文件路径
    :param time_unit: 时间单位，"ms"为毫秒（默认），"s"为秒
    """
    def format_time(time_val):
        """将整数时间转换为SRT时间格式 (HH:MM:SS,mmm)"""
        if time_unit == "s":  # 秒转毫秒
            time_val = int(time_val * 1000)
        hours, rem = divmod(time_val, 3600000)
        minutes, rem = divmod(rem, 60000)
        seconds, milliseconds = divmod(rem, 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    with open(output_file, 'w', encoding='utf-8-sig') as f:  # UTF-8带BOM
        for idx, (start, end, text) in enumerate(subtitles, 1):
            # 写入序号
            f.write(f"{idx}\n")
            # 写入时间轴
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            # 写入字幕文本（支持多行）,添加顶部居中定位标签
            f.write(f"{{\\an8}}{text.strip()}\n\n")  # 结尾双换行分隔条目