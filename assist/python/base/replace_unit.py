import re
#变量
variable_reg=r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
#数值
num_reg=r'\d+\.\d+|\d+|-\d+\.\d+|-\d+'
#其他符号
symbol_reg=r'[^a-zA-Z0-9_]+'

def has_variable(s):
    return  bool(re.findall(variable_reg, s))
def split_string_regex(org):
    """使用正则表达式将字符串打散成满足和不满足 C++ 变量名要求的子串"""
    # 正则表达式模式：匹配 C++ 变量名或非 C++ 变量名的子串
    # pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\d+\.\d+|\d+|[^a-zA-Z0-9_]+'
    pattern = f"{variable_reg}|{num_reg}|{symbol_reg}"
    return re.findall(pattern, org)

def replace_text(org, replacements):
    """根据字典进行替换"""
    parts = split_string_regex(org)
    replaced_parts = [replacements.get(part, part)  for part in parts]
    return ''.join(map(str, replaced_parts))



if __name__ == '__main__':

    # 示例用法
    org = [
        "((i*l-d-f)+(h-1.3)*i)/(l+(1-i)*(h-1))",
        "-(l*i*j+(d+f)*(1-j))/((1-j)*(h-1)+l)"
        ]
    replacements = {
    "k":"self.org_discont",
    "a":"self.org_price",
    "b":"self.normal_price",
    "c":"self.real_price",
    "j":"self.normal_cut_ratio",
    "i":"self.normal_coupon",
    "d":"self.profit",
    "f":"self.fix_cost",
    "h":"self.real_cut_ratio",
    "l":"self.brokerage_cut_ratio",
    "m":"self.brokerage_cut",
    "g":"self.real_cut_cost",
    "e":"self.final_cost",
    }

    for item in org:
        print(  f"org:{item} -> replaced:{replace_text(item, replacements)}" )
    
