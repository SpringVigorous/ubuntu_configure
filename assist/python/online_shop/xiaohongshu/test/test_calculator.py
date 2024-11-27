import os
import sys
import pandas as pd



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from price_calculator import PriceCalculator
from base.math_tools import ceil_5



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

    org_price=ceil_5(float(calculator.result("定价")))
    normal_price=ceil_5(float(calculator.result("一口价")))
    
    lst.append(calculator.calculate_by_org_price(org_price))
    calculator.show_formulas()
    
    lst.append(calculator.calculate_by_normal_price(normal_price))
    calculator.show_formulas()

    df=pd.DataFrame(lst)
    df.to_excel(r"E:\花茶\价格\temp\price.xlsx",index=False)
