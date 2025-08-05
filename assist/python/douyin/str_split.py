import re

def replace_punctuation_with_newline(text):
    # 使用正则表达式匹配一个或多个连续的标点符号
    result = re.sub(r'[^\w\s]', '\n', text)
    # 使用正则表达式将多个连续的换行符替换为一个换行符
    # result = re.sub(r'\n+', '\n', result)
    result = re.sub(r'\s*\n\s*', '\n', result)
    return result

# 示例用法
input_text = """熬夜盯屏幕？眼睛干到眨不动？中伏必备的黄芪黄精水，专治上班疲劳，手脚没劲；黄芪4克，黄精5克，太子参5克，何首乌2克，红枣3克，食材全部倒入养生壶，加800毫升水，烧开后在煮10分钟，黄精太子参的清甜中混合着枣香，中伏坚持喝，精力充沛 干活不累"""
output_text = replace_punctuation_with_newline(input_text)
print(output_text)

