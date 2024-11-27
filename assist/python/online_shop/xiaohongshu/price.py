import os
import sys
import pandas as pd
import math


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from base.formula_calculator import *
from base.replace_unit import *


symbols_dict={
    'a':"成本",
    'b':"利润",
    'c':"实付款",
    'd':"佣金基数",
    'e':"收入金额",
    'f':"一口价",
    'g':"定价",
    'i':"固定成本",
    'j':"浮动成本",
    'k':"物料费",
    'l':"快递费",
    'm':"运费险",
    'n':"佣金",
    'o':"佣金比率",
    'p':"提现手续费",
    'q':"提现费率",
    'r':"总优惠",
    's':"平台券",
    't':"商家优惠",
    'u':"商家券",
    'v':"一口价折扣比率",
    'w':"定价折扣",
    'y':"收款抵扣后",
}
class PriceCalculator:

    _common_formulas=[
        "i=k+l+m",
        "a=i+j",
        "j=n+p",
        "n=d*o",
        "p=y*q",
        "d=c+s",
        "e=d-n",
        "y=e-m",
        "t=u+f*v",
        "r=t+s",
    ]
    _profit_formulas=[
        "c=(m*q-b-i)/(o+(1-o)*q-1)-s",
        "f=(u+s+c)/(1-v)",
        "g=f/w",
    ]
    #共有的
    _org_normal_formulas=[
        "c=f-r",
        "b=d-a",
    ]
    
    _org_formulas=[
        "f=g*w",
    ]
    _normal_formulas=[
        "g=f/w",
    ]
    _org_formulas.extend(_org_normal_formulas)
    _normal_formulas.extend(_org_normal_formulas)
    
    
    
    """
    #ship_insure:运费险:m
    #cash_out_ratio:提现费率:q
    #material_cost:物料费:k
    #ship_fee:快递费:l
    #platform_coupon:平台券:s
    #seller_coupon:商家券:u
    #normal_cut_ratio:一口价折扣比率:v
    #brokerage_cut_ratio:佣金基数:o
    #org_discont:定价折扣（8折扣->.8):w
    """
    def __init__(self,material_cost:float=10,ship_fee:float=8,seller_coupon:float=20,platform_coupon:float=5,cash_out_ratio:float=.005,ship_insure:float=1.5,normal_cut_ratio:float=.05,brokerage_cut_ratio:float=.1,org_discont:float=.9):
       
        self._calculator=FormulaCalculator()
        self._calculator.set_symbols(symbols_dict)
        
        self._calculator.add_variable("m",ship_insure)
        self._calculator.add_variable("q",cash_out_ratio)
        self._calculator.add_variable("k",material_cost)
        self._calculator.add_variable("l",ship_fee)
        self._calculator.add_variable("s",platform_coupon)
        self._calculator.add_variable("u",seller_coupon)
        self._calculator.add_variable("v",normal_cut_ratio)
        self._calculator.add_variable("o",brokerage_cut_ratio)
        self._calculator.add_variable("w",org_discont)
        
        self._calculator.add_formlua(PriceCalculator._common_formulas)

    def _calculate_impl(self,key:str,val:float,formulas:list[str]):
        self._calculator.add_variable(key,val)
        self._calculator.add_formlua(formulas)
        self._calculator.calculate()
        return self._calculator.info()

    #利润作为已知条件
    def calculate_by_profit(self,profit:float=5):
        return self._calculate_impl("b",profit,PriceCalculator._profit_formulas)

    # 定价作为已知条件
    def calculate_by_org_price(self,org_price:float):
        return self._calculate_impl("g",org_price,PriceCalculator._org_formulas)
    #一口价作为已知条件
    def calculate_by_normal_price(self,normal_price:float):
        return self._calculate_impl("f",normal_price,PriceCalculator._normal_formulas)

    
    def result(self,key,default_value=0):
        return self._calculator.result(key,default_value)
    
    def formula(self,key,default_value=""):
        return self._calculator.formula(key,default_value)
    def show_formulas(self):
        self._calculator.show_formulas()
        
    def show_results(self):
        self._calculator.show_results()
    
def round_up_to_5(n):
    return math.ceil(n / 5) * 5

if __name__=="__main__":
    material_cost:float=10
    ship_fee:float=8
    seller_coupon:float=5
    platform_coupon:float=0
    cash_out_ratio:float=.005
    ship_insure:float=1.5
    normal_cut_ratio:float=.05
    brokerage_cut_ratio:float=.1
    org_discont:float=.8

    calculator=PriceCalculator(material_cost,
            ship_fee,
            seller_coupon,
            platform_coupon,
            cash_out_ratio,
            ship_insure,
            normal_cut_ratio,
            brokerage_cut_ratio,
            org_discont,)



    profit=5
    lst=[]

    lst.append(calculator.calculate_by_profit(profit))
    
    print(calculator.formula("实付款"))
    calculator.show_formulas()
    

    
    calculator.show_formulas()

    org_price=round_up_to_5(float(calculator.result("定价")))
    normal_price=round_up_to_5(float(calculator.result("一口价")))
    
    lst.append(calculator.calculate_by_org_price(org_price))
    calculator.show_formulas()
    
    lst.append(calculator.calculate_by_normal_price(normal_price))
    calculator.show_formulas()

    df=pd.DataFrame(lst)
    df.to_excel(r"E:\花茶\价格\temp\price.xlsx",index=False)