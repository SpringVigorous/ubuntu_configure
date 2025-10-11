import re
from base.replace_unit import *
from collections import defaultdict
def extract_variable_and_expression(formula):
    """
    提取公式中的变量名和表达式部分。
    :param formula: str, 公式字符串
    :return: tuple, (变量名, 表达式)
    """
    # 使用正则表达式以 "=" 为分隔符分割公式
    match = re.split(r'\s*=\s*', formula, maxsplit=1)
    if len(match) != 2:
        raise ValueError(f"无效的公式格式: {formula}")
    
    variable_name, expression = match
    return variable_name.strip(), expression.strip()
def evaluate_formula(formula, variables):
    """
    评估公式并返回结果。
    :param formula: str, 公式字符串
    :param variables: dict, 变量及其值的字典
    :return: 计算结果
    """
    # 替换公式中的变量

    formula = replace_text(formula,variables)
    success=not has_variable(formula)
    if  success:
        # 评估公式
        try:
            result:float = eval(formula)
        except Exception as e:
            raise ValueError(f"无法评估公式 {formula}: {e}")
    
        return (True,result) 

    return (False,formula)
def formula_calculate(init_formulas, variables:dict={}):
    """
    计算一系列公式。
    :param formulas: list of str, 公式列表
    :param initial_values: dict, 初始变量及其值的字典
    :return: 更新后的变量字典
    """
    formulas=init_formulas.copy()
    times=0
    count=len(formulas)
    while formulas and times<count*2:
        new_formulas = {}
        for key, formula in formulas.items():
            success, result = evaluate_formula(formula, variables)
            if success:
                variables[key] = result
            else:
                new_formulas[key] = result

        formulas = new_formulas
        times+=1
    
    variables.update(formulas)
    return variables

def formula_dict(org_formulas:list=None):
    if org_formulas is None:
        return {}
    formulas_dic={}
    for mula in org_formulas:
        key,val=extract_variable_and_expression(mula)
        formulas_dic[key]=val
    return formulas_dic
    
class FormulaCalculator:
    #formulas的各项是字符串类型，格式为“变量名=表达式”，例如“a = 1 + 2”
    def __init__(self, formulas:list=None):
        self.set_formulas(formulas)

    def add_formlua(self, formula:str|list[str]):
        
        def add(one_formula):
            key,val=extract_variable_and_expression(one_formula)
            self._formulas[key]=val
        
        if isinstance(formula,list):
            for mula in formula:
                add(mula)
        else:
            add(formula)

    def set_symbols(self, symbol_dic:dict):
        self._symbol_dic = symbol_dic
        
    @property
    def has_symbols(self)->bool:
        return bool(self._symbol_dic)
        
    @property
    def word_symbols(self)->dict:
        return {v: k for k, v in self._symbol_dic.items()}
        
    
    def add_variable(self, variable_name, value:str|int|float):
        self._formulas[variable_name] = str(value)
        
    def set_formulas(self, formulas=None):
        self._formulas:dict = formula_dict(formulas)
        self._result:dict={}
        self._symbol_dic:dict={}
        
    #删除某个已确定的公式，通过key值删除
    def remove_formula(self,key):
        if key in self._formulas:
            del self._formulas[key]
    
    def calculate(self):
        variable_lst={}
        self._result= formula_calculate(self._formulas,variable_lst)
        return self._result
    def _org_key(self,symbol_key):
        return self.word_symbols.get(symbol_key,symbol_key)
    
    def result(self,key,default_value=0):
        return self.result_org(self._org_key(key),default_value)
    def formula(self,key,default_value=""):
        val= self.formula_org(self._org_key(key),default_value)
        if self.has_symbols:
            val=replace_text(val,self._symbol_dic)
        return val
    def result_org(self,key,default_value=0):
        return self._result.get(key,default_value)
    def formula_org(self,key,default_value=""):
        return self._formulas.get(key,default_value)
    
    
    def info(self,include_org_formula:bool=False, checked_formula:bool=False):
        

        # 创建一个默认值为 list 的字典
        merged_dict = defaultdict(list)

        # 将字典 a 的键值对添加到 merged_dict 中
        for key, value in self._formulas.items():
            merged_dict[key].append(value)

        # 将字典 b 的键值对添加到 merged_dict 中
        for key, value in self._result.items():
            merged_dict[key].append(value)

        result_dict={}
        # 打印合并后的字典
        for key in merged_dict:
            symbol=self._symbol_dic.get(key,"") if self._symbol_dic else ""
            if include_org_formula:
                symbol=f"{symbol}:{key}"
            val=merged_dict[key][-1] if not checked_formula else "=".join(map(str, merged_dict[key]))
            result_dict[symbol]=val
        return result_dict


    #展示 公式：方便查找公式是否正确
    def show_formulas(self,use_symbol_name=True):
        for key,val in self._formulas.items():
            if self.has_symbols and use_symbol_name:
                key=replace_text(key, self._symbol_dic)
                val=replace_text(val, self._symbol_dic)
            print(f"{key} = {val}")
        print("-"*50)
    def show_results(self,use_symbol_name=True):
        for key,val in self._result.items():
            if self.has_symbols and use_symbol_name:
                key=replace_text(key, self._symbol_dic)
                val=replace_text(str(val), self._symbol_dic)
            print(f"{key} = {val}")
        print("-"*50)



if __name__ == '__main__':
    # 示例用法
    formulas = [
        "a = 1 + 2",
        "b = a * 3",
        "c = b + 5",
        "d = c / 2+a-b*c",
        "e=a+c-d"
    ]

    calculator = FormulaCalculator(formulas)
    calculator.calculate()
    calculator.info()
    print("------------------------")
    calculator.add_formlua("a = 4+10")
    calculator.calculate()
    calculator.info()
    print(calculator.result("d"))
    print(calculator.formula("d"))

    
    
