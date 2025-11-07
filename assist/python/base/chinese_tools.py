
from base.collect_tools import remove_consecutive_duplicates

from pathlib import Path

def has_chinese(path: str | Path) -> bool:
    """
    精准判断路径是否包含汉字（排除其他非 ASCII 字符）
    
    参数：
        path: 路径（字符串或 Path 对象）
    返回：
        True: 含汉字；False: 不含汉字
    """
    path_str = str(path)
    for char in path_str:
        # 汉字的 Unicode 编码范围：0x4E00 ~ 0x9FFF
        if 0x4E00 <= ord(char) <= 0x9FFF:
            return True
    return False
def chinese_to_arabic(chinese_num):
    # 基础数字映射
    char_to_digit = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, 
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9
    }
    
    # 单位映射表（按层级从高到低）
    unit_levels = [
        ('京', 10**16),
        ('兆', 10**12),
        ('亿', 10**8),
        ('万', 10**4),
        ('千', 1000),
        ('百', 100),
        ('十', 10)
    ]
    
    # 特殊处理：十、百、千前面省略"一"的情况
    implied_one_units = {'十', '百', '千', '万', '亿'}
    
    # 递归解析函数
    def parse_number(s, units):
        if not s:
            return 0
            
        # 如果当前单位列表为空，直接解析基本数字
        if not units:
            return parse_basic(s)
            
        unit_char, unit_value = units[0]
        remaining_units = units[1:]
        
        # 查找当前单位在字符串中的位置
        pos = s.find(unit_char)
        if pos == -1:
            # 当前单位不存在，尝试下一个单位
            return parse_number(s, remaining_units)
        
        # 分割字符串
        left_part = s[:pos]
        right_part = s[pos+len(unit_char):]
        
        # 解析单位左侧部分
        if left_part:
            left_value = parse_number(left_part, remaining_units)
        else:
            # 处理省略"一"的情况（如"十万"）
            left_value = 1 if unit_char in implied_one_units else 0
        
        # 解析单位右侧部分
        right_value = parse_number(right_part, units)
        
        # 计算当前单位的值
        current_value = left_value * unit_value
        
        # 返回总和
        return current_value + right_value
    
    # 解析基本数字（不含大单位）
    def parse_basic(s):
        if not s:
            return 0
            
        # 处理纯零
        if s == "零":
            return 0
            
        value = 0
        last_digit = 0
        has_unit = False
        
        for char in s:
            if char in char_to_digit:
                # 保存上一个数字
                if last_digit > 0:
                    value += last_digit
                    last_digit = 0
                last_digit = char_to_digit[char]
            elif char in ['十', '百', '千']:
                # 处理基本单位
                unit_value = 10 if char == '十' else 100 if char == '百' else 1000
                
                # 处理省略"一"的情况
                if last_digit == 0:
                    last_digit = 1
                
                value += last_digit * unit_value
                last_digit = 0
                has_unit = True
            # 忽略"零"
        
        # 加上最后的个位数
        return value + last_digit
    
    # 主函数
    if chinese_num == "零":
        return 0
        
    # 从最高单位开始解析
    return parse_number(chinese_num, unit_levels)
def arabic_to_chinese(num):
    # 基础数字字符
    digits = "零一二三四五六七八九"
    
    # 单位系统：万亿(10^12), 亿(10^8), 万(10^4)
    units = [
        (10**8, "亿"),
        (10**4, "万")
    ]
    
    def arabic_to_chinese_imp(num):
    
        """
        按亿级单位分段的精确转换函数
        """
        if num == 0:
            return "零"
        
        
        def convert_under_10000(n,has_high=True):
            """转换0-9999范围内的数字"""
            if n == 0:
                return ""
            if n < 0 or n >= 10000:
                raise ValueError("必须0-9999之间的数字")
            
            result = []
            # 千位处理
            qian = n // 1000
            if qian > 0:
                result.append(digits[qian] + "千")
                n %= 1000
            elif has_high and (n > 0):  # 之前有数字且当前或之后有非零
                result.append("零")
            # 百位处理
            bai = n // 100
            if bai > 0:
                result.append(digits[bai] + "百")
                n %= 100
            elif result and (n > 0):  # 之前有数字且当前或之后有非零
                result.append("零")
            
            # 十位处理
            shi = n // 10
            if shi > 0:
                # 特殊处理十位一的情况：当十位是第一个非零数字时
                if shi == 1 and (not result or result[-1] == "零"):
                    result.append("十")
                else:
                    result.append(digits[shi] + "十")
                n %= 10
            elif result and (n > 0):
                result.append("零")
            
            # 个位处理
            if n > 0:
                result.append(digits[n])
            
            result=remove_consecutive_duplicates(result)
            
            return ''.join(result)

        result = []
        
        # 处理100万亿及以上的部分
        for unit_val, unit_name in units:
            if num >= unit_val:
                # 取出当前单位部分
                part = num // unit_val
                num %= unit_val
                
                if part > 0:
                    # 递归转换当前部分（可以包含其他级别单位）
                    result.append(arabic_to_chinese_imp(part) + unit_name)
                    
                    # 特别处理连续零的位置
                    if num and (num < unit_val // 100):
                        result.append("零")

        # 处理小于10000的部分
        if num > 0:
            result.append(convert_under_10000(num))
        elif not result and num == 0:
            return "零"

        result=remove_consecutive_duplicates(result)
        
        # 处理特殊情况："一十"开头的优化
        final_str = ''.join(result)
        if final_str.startswith("一十"):
            final_str = final_str[1:]
        return final_str
    
    final_str = arabic_to_chinese_imp(num)
    while "零零" in final_str:
        final_str=final_str.replace("零零", "零")
    return final_str if final_str[0]!="零" else final_str[1:]
if __name__ == '__main__':
    # 测试示例
    tests = [
        ("十万亿零八万零九", 123456789),
        
        ("三百零五万零二十亿零七百零二",305002000000702),
        ("三百零五万零二十亿零五百零八万七千零二",305000005087002),
        ("十", 10),
        ("一百", 100),
        ("一千零一", 1001),
        ("一万", 10000),
        ("十万亿", 10000000000000),
        ("三十", 30),
        ("三百万", 3000000)
    ]

    for test, expected in tests:
        arabic_result = chinese_to_arabic(test)
        print(f"\"{test}\" => {arabic_result} (预期: {expected}),结果：{arabic_result == expected}")
        
        chinise_result=arabic_to_chinese(arabic_result)
        
        print(f"\"{arabic_result}\" => {chinise_result} (预期: {test}),结果：{chinise_result == test}")
        
        
    
    