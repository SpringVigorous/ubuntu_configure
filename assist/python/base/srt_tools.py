import re
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
            
            
            
"""
1
00:01:21,280 --> 00:01:28,080
Tantra is the secret of the union between Shiva and Shakti‚ between man and woman． 
坦陀罗是湿婆和沙克蒂之间，男人和女人之间结合的秘密˳

2
00:01:29,100 --> 00:01:37,280
And although th​‌​‌​​‌‌​​‌‌​​‌‌‌​‌‌‌‌​‌​​‌‌‌‌​‌​​‌‌​​‌‌​​​‌​​‌‌‌‌‌​​​‌‌‌‌​‌‌‌​‌‌​​‌​​‌‌​‌​‌‌‌​‌​​‌‌‌‌​‌​​​‌​​‌‌‌‌‌‌​​‌‌​‌‌‌​​‌‌​‌​‌​​‌‌‌‌‌‌​​‌‌​​​‌​​‌‌​​‌‌‌‌​‌‌‌​‌​​‌‌‌​‌‌​​‌‌​‌​‌‌‌​‌​‌‌‌‌‌​‌​‌​‌​​‌‌‌‌‌​​​‌‌‌‌​‌​​‌‌‌‌‌​​​‌‌‌​‌‌​​‌‌‌​‌‌‌‌​‌‌‌‌‌​​‌‌‌​‌‌​​‌‌‌‌‌‌​​‌‌​​‌‌​​‌‌​​‌‌‌‌​‌‌‌​‌​​‌‌‌​​‌‌‌​‌‌​​‌​​‌‌‌​​‌​​‌‌​‌‌​​​‌‌​​‌‌​​‌‌​​​‌​​‌‌​‌​‌‌‌​‌‌‌‌‌​​‌‌‌‌​‌​​‌‌‌​​‌‌‌​‌​‌‌‌​​‌‌​‌‌‌‌‌​‌‌‌‌​​​‌‌​​‌‌‌‌​‌‌‌​‌​​‌‌​​​‌​​‌‌​‌​‌​​‌‌‌​‌‌‌‌​‌​‌‌‌​​‌‌‌‌‌​​​‌‌​‌‌‌‌‌​‌‌‌​‌​​‌‌‌‌​‌‌‌​‌‌‌‌​​​‌‌​‌​‌‌‌​‌‌​​‌​​‌‌​‌​‌​​‌‌​‌‌‌​​‌‌‌‌​‌​​‌‌​​‌‌‌‌​‌​‌​‌‌‌​‌‌‌​‌‌‌​‌​‌‌​​​‌‌‌​‌‌‌‌​‌​​‌‌‌‌​‌​‌​‌‌‌​‌​​‌‌‌‌​‌​‌‌‌‌‌​‌‌‌​‌‌‌​‌​‌​‌​​‌‌​‌​‌‌‌​‌‌​​‌‌‌​‌‌‌​‌‌‌​‌‌‌​‌​​‌‌‌‌​‌​​‌‌‌​​‌‌‌​‌​​‌‌​​‌‌‌​​‌​​‌‌‌‌​‌​​‌‌​‌‌‌​​‌‌‌‌​‌‌‌​‌​‌‌‌‌‌​‌​​‌‌‌‌​‌​‌‌‌‌‌​‌​‌‌​​​‌‌​‌‌‌‌‌​‌‌‌​‌‌‌​‌‌‌​‌‌‌​‌‌‌​‌‌‌​‌​​‌‌​​‌‌​‌​‌​​‌‌​​‌‌‌‌​‌‌​​‌​​‌‌​‌​‌‌‌​‌‌​‌‌‌‌​‌​‌​‌‌‌​‌​‌‌‌‌‌​‌​‌​‌‌‌​‌‌‌‌​​​‌‌‌‌​‌​​‌‌‌‌​‌​​‌‌‌​​‌‌‌​‌‌‌‌​​​‌‌‌​‌‌‌‌​‌‌‌​‌‌‌​‌‌‌​‌‌‌​‌‌​​‌​​‌‌​‌​‌‌‌​‌​‌‌‌​​‌‌​‌‌​​​‌‌‌‌​‌‌‌​‌​‌‌‌​​‌‌‌‌‌​​​‌‌​‌​‌​​‌‌‌‌​‌​​‌‌‌​‌‌‌‌​‌‌​‌‌‌‌​‌‌​​‌‌‌​‌​‌‌‌‌‌​‌‌​‌‌‌‌​‌‌​‌‌‌‌​‌‌‌‌‌​​‌‌‌‌‌‌​​‌‌​‌‌‌​​‌‌‌​‌‌‌‌​‌‌​‌‌‌‌​‌‌​​‌​​‌‌​​‌‌​​‌‌‌​​‌​​‌‌‌​​‌​​‌‌​‌​‌‌‌​‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌e origins of Tantra go back many thousands of years‚ tantra is as relevant today as it always has been． 
尽管密宗的起源可以追溯到几千年前，但今天密宗仍然一如既往地具有相关性˳
"""

def srt_to_txt(srt_path, txt_path):
    """
    提取.srt字幕内容到.txt，每条一行，并去除{...}格式标签
    
    参数：
        srt_path: .srt文件路径
        txt_path: 输出.txt文件路径
    """
    # 正则表达式：匹配以{开头、}结尾的所有内容（包括{}本身）
    tag_pattern = re.compile(r'\{.*?\}', re.DOTALL)  # re.DOTALL确保.匹配换行符（应对多行标签）
    
    subtitles = []
    current_sub = []
    
    with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()  # 去除首尾空格和换行
            
            # 跳过序号（纯数字）和时间轴（含-->）
            if line.isdigit() or '-->' in line:
                continue
            
            # 遇到空行，结束当前字幕处理
            if not line:
                if current_sub:
                    # 合并当前字幕的多行内容，去除多余空格
                    sub_text = ' '.join(current_sub).strip()
                    # 去除可能残留的连续空格（如多个标签被删除后）
                    sub_text = re.sub(r'\s+', ' ', sub_text)
                    subtitles.append(sub_text)
                    current_sub = []
            else:
                # 先去除当前行中的{...}标签，再添加到临时列表
                line_clean = tag_pattern.sub('', line).strip()
                if line_clean:  # 避免添加空行
                    current_sub.append(line_clean)
    
    # 处理最后一条字幕（可能无结尾空行）
    if current_sub:
        sub_text = ' '.join(current_sub).strip()
        sub_text = re.sub(r'\s+', ' ', sub_text)
        subtitles.append(sub_text)
    
    # 写入.txt
    with open(txt_path, 'w', encoding='utf-8') as f:
        for sub in subtitles:
            f.write(sub + '\n')

# 示例用法
if __name__ == "__main__":
    
    from base import srt_files,logger_helper
    from pathlib import Path
    import os
    for srt_file in srt_files(r"E:\旭尧"):
        org_path = Path(srt_file)    # 替换为你的.srt路径
        txt_file = org_path.parent.parent / f"srt_txt_{org_path.parent.stem}" / f"{org_path.stem}.txt" # 输出的.txt路径
        os.makedirs(txt_file.parent, exist_ok=True)
        srt_to_txt(srt_file, txt_file)
