import os
import re

# 目录路径
directory = r'F:\教程\多肉\哔哩哔哩视频'

# 正则表达式模式
# pattern = re.compile(r'(第\d+|第一|第二|第三|第四|第五|第六|第七|第八|第九|第十)(.*)')
pattern = re.compile(r'(一|二|三|四|五|六|七|八|九|十)')

# 需要排除的行格式
exclude_pattern = re.compile(r'^\d+$|^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}')

dest_path=os.path.join(directory, 'title')
if not os.path.exists(dest_path):
    os.makedirs(dest_path)
# 遍历目录中的所有.srt文件
for filename in os.listdir(directory):
    if filename.endswith('.srt'):
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # 按行分割文件内容
            lines = content.split('\n')
            
            # 用于存储字幕内容
            subtitles = []
            
            for line in lines:
                # 排除编号和时间戳行
                if not exclude_pattern.match(line.strip()):
                    subtitles.append(line.strip())
            


                        
            
            
            
            # 合并连续的字幕行
            merged_subtitles = []
            current_subtitle = ''
            
            for subtitle in subtitles:
                if pattern.search(subtitle):
                    if current_subtitle:
                        merged_subtitles.append(current_subtitle)
                        current_subtitle = ''
                    else:
                        index=subtitles.index(subtitle)
                        if index>1:
                            merged_subtitles.append(" ".join( subtitles[:index]))
                    current_subtitle = subtitle+":"
                else:
                    if current_subtitle:
                        current_subtitle += ' ' + subtitle
            
            if current_subtitle:
                merged_subtitles.append(current_subtitle)
            
            

            new_filepath = os.path.join(dest_path, filename.replace('.srt', '_title.txt'))
            with open(new_filepath, 'w', encoding='utf-8') as new_file:
               new_file.write( "\n".join(merged_subtitles))
