import os
def remove_english_lines(input_file, output_file):
    """
    从双语SRT字幕文件中删除英语行（保留中文行）
    参数：
        input_file: 输入SRT文件路径
        output_file: 输出SRT文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割字幕块（每个字幕段）
    blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
    processed_blocks = []
    
    for block in blocks:
        lines = block.split('\n')
        # 仅处理包含完整结构的字幕块（序号+时间轴+至少两行文本）
        if len(lines) >= 4:
            # 重组块内容：序号(0) + 时间轴(1) + 中文行(3) + 后续行(4+)
            new_lines = lines[0:2] + lines[3:]
            processed_blocks.append('\n'.join(new_lines))
        else:
            # 保留不符合结构的原始块（避免数据丢失）
            processed_blocks.append(block)
    
    # 用双换行符重新连接所有块
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(processed_blocks))

# 使用示例
cur_dir=r"F:\数据库"
remove_english_lines(os.path.join(cur_dir,"印度密宗.srt"), os.path.join(cur_dir,"印度密宗_new.srt"))