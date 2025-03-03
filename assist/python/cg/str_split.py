import re

def replace_punctuation_with_newline(text):
    # 使用正则表达式匹配一个或多个连续的标点符号
    result = re.sub(r'[^\w\s]', '\n', text)
    # 使用正则表达式将多个连续的换行符替换为一个换行符
    # result = re.sub(r'\n+', '\n', result)
    result = re.sub(r'\s*\n\s*', '\n', result)
    return result

# 示例用法
input_text = """亲爱的朋友们，今天给大家推荐一家超棒的酒店——臻月唐酒店新天地店！
 
这是一家充满中式唐文化韵味的酒店，步入其中，仿佛穿越回了唐朝，能让您沉浸式感受唐文化的魅力。
 
而且我们现在有超值的优惠活动，只需 99 元，您就可以享受 2 天 1 夜的舒适住宿。酒店干净卫生，让您住得安心、舒心。另外，我们还提供免费停车服务，为您的出行解决后顾之忧。
 
无论是休闲度假还是商务出行，臻月唐酒店新天地店都是您的理想之选。别再犹豫啦，赶快预定，来体验这独特的住宿之旅吧！"""
output_text = replace_punctuation_with_newline(input_text)
print(output_text)

