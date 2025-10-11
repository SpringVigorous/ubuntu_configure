import os
import sys
import pandas as pd


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


    calculator=PriceCalculator(material_cost,
            ship_fee,
            seller_coupon,
            platform_coupon,
            cash_out_ratio,
            ship_insure,
            normal_cut_ratio,
            brokerage_cut_ratio,
            )



    profit=5
    lst=[]

    lst.append(calculator.calculate_by_profit(profit))
    
    print(calculator.formula("实付款"))
    calculator.show_formulas()
    

    
    calculator.show_formulas()

    normal_price=ceil_5(float(calculator.result("定价")))

    
    lst.append(calculator.calculate_by_normal_price(normal_price))
    calculator.show_formulas()

    df=pd.DataFrame(lst)
    df.to_excel(r"E:\花茶\价格\temp\price.xlsx",index=False)
