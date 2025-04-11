import re

def replace_punctuation_with_newline(text):
    # 使用正则表达式匹配一个或多个连续的标点符号
    result = re.sub(r'[^\w\s]', '\n', text)
    # 使用正则表达式将多个连续的换行符替换为一个换行符
    # result = re.sub(r'\n+', '\n', result)
    result = re.sub(r'\s*\n\s*', '\n', result)
    return result

# 示例用法
input_text = """家人们，最近打算出游赏樱的，一定别错过鼋头渚的晚樱！早樱、中樱虽美，但已悄然退场，好在晚樱接力绚烂。当下，正是观赏晚樱的黄金时期。踏入鼋头渚，大片粉樱如梦幻云霞，微风轻拂，花瓣飘然而下，浪漫至极。要是前面的花期没赶上，这次晚樱可千万别错过，赶紧安排上，赴一场春日之约！"""
output_text = replace_punctuation_with_newline(input_text)
print(output_text)

