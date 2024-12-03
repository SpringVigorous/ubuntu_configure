

#normal_price:定价;b
#real_price:到手价;c
#normal_cut_ratio:满减折扣比率（8折扣->.2);j
#normal_coupon:优惠券金额;i
#profit:利润;d
#fix_cost:固定成本;f
#real_cut_ratio:到手价扣点比率，浮动成本率;h
#brokerage_cut_ratio:佣金比例（基数：定价);l
#brokerage_cut:佣金;m
#real_cut_cost:到手价扣点成本;g
#final_cost:最终成本;e

#到手价->定价
def real_to_normal(real_price,normal_cut_ratio,normal_coupon):
    return (real_price +normal_coupon ) / (1-normal_cut_ratio)

#定价->到手价
def normal_to_real(normal_price,normal_coupon,normal_cut_ratio):
    return normal_price * (1-normal_cut_ratio) - normal_coupon
#（利润，固定成本，扣点成本）  到手价
def cal_real_price(profit,fix_cost,real_cut_ratio):
    return (profit + fix_cost)/(1 - real_cut_ratio)


#定价
def cal_normal_price(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon):
    val=cal_real_price(profit,fix_cost,real_cut_ratio)
    return real_to_normal(val,normal_coupon,normal_cut_ratio)






if __name__=="__main__":


   pass