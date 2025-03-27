import re

def replace_punctuation_with_newline(text):
    # 使用正则表达式匹配一个或多个连续的标点符号
    result = re.sub(r'[^\w\s]', '\n', text)
    # 使用正则表达式将多个连续的换行符替换为一个换行符
    # result = re.sub(r'\n+', '\n', result)
    result = re.sub(r'\s*\n\s*', '\n', result)
    return result

# 示例用法
input_text = """宝子们，来鼋头渚赴一场夜樱之约！夜幕降临，华灯初上，粉色樱花在灯光映衬下如梦如幻，仿佛踏入童话世界，浪漫到极致，千万别错过这限定美景。"""
output_text = replace_punctuation_with_newline(input_text)
print(output_text)

