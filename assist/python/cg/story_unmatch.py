#用正则表达式查找，eg:从以下 找到 ["我在乱世娶妻长生","第两百一十七章 婳","https://www.nlxs.org/104/104522/2/"]
# 2025-03-04 14:26:44,791-WARNING-Thread ID: 9580-【我在乱世娶妻长生】-【未匹配标题: 第两百一十七章 婳】详情：https://www.nlxs.org/104/104522/2/,耗时：0.000秒 
import re

# 输入字符串
input_string = '2025-03-04 14:26:44,791-WARNING-Thread ID: 9580-【我在乱世娶妻长生】-【未匹配标题: 第两百一十七章 婉】详情：https://www.nlxs.org/104/104522/2/,耗时：0.000秒'

# 正则表达式模式
pattern = r'【([^】]+)】-【未匹配标题: ([^】]+)】详情：([^,]+)'

# 查找匹配项
match = re.search(pattern, input_string)

if match:
    book_title = match.group(1)
    chapter_title = match.group(2)
    url = match.group(3)
    result = [book_title, chapter_title, url]
    print(result)
else:
    print("未找到匹配项")
    
    
    
