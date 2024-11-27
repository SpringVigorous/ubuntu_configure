import os
import sys



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from price_base import PriceCalculatorBase
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
class PriceCalculator(PriceCalculatorBase):

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
    
    #material_cost:物料费:k
    #ship_fee:快递费:l
    #seller_coupon:商家券:u
    #platform_coupon:平台券:s
    #cash_out_ratio:提现费率:q
    #ship_insure:运费险:m
    #normal_cut_ratio:一口价折扣比率:v
    #brokerage_cut_ratio:佣金比率:o
    #org_discont:定价折扣（8折扣->.8):w
    """
    def __init__(self,material_cost:float=10,ship_fee:float=8,seller_coupon:float=20,platform_coupon:float=5,cash_out_ratio:float=.005,ship_insure:float=1.5,normal_cut_ratio:float=.05,brokerage_cut_ratio:float=.1,org_discont:float=.9):
        super().__init__()

        self.set_symbols(symbols_dict)
        
        self.add_variable("m",ship_insure)
        self.add_variable("q",cash_out_ratio)
        self.add_variable("k",material_cost)
        self.add_variable("l",ship_fee)
        self.add_variable("s",platform_coupon)
        self.add_variable("u",seller_coupon)
        self.add_variable("v",normal_cut_ratio)
        self.add_variable("o",brokerage_cut_ratio)
        self.add_variable("w",org_discont)
        
        self.add_formlua(PriceCalculator._common_formulas)

    #利润作为已知条件
    def calculate_by_profit(self,profit:float=5):
        return self._calculate_impl("b",profit,PriceCalculator._profit_formulas)

    # 定价作为已知条件
    def calculate_by_org_price(self,org_price:float):
        return self._calculate_impl("g",org_price,PriceCalculator._org_formulas)
    #一口价作为已知条件
    def calculate_by_normal_price(self,normal_price:float):
        return self._calculate_impl("f",normal_price,PriceCalculator._normal_formulas)

    
    
