#org_discont:定价折扣（8折扣->.8);k
#org_price:定价;a
#normal_price:一口价;b
#real_price:到手价;c
#normal_cut_ratio:每满减折扣比率（8折扣->.2);j
#normal_coupon:优惠券金额;i
#profit:利润;d
#fix_cost:固定成本;f
#real_cut_ratio:到手价扣点比率，浮动成本率;h
#brokerage_cut_ratio:佣金比例（基数：一口价);l
#brokerage_cut:佣金;m
#real_cut_cost:到手价扣点成本;g
#final_cost:最终成本;e
#一口价->定价
def normal_to_org(normal_price,org_discont):
    return normal_price / org_discont
#定价->一口价
def org_to_normal(org_price,org_discont):
    return org_price * org_discont  
#到手价->一口价
def real_to_normal(real_price,normal_cut_ratio,normal_coupon):
    return (real_price +normal_coupon ) / (1-normal_cut_ratio)

#一口价->到手价
def normal_to_real(normal_price,normal_coupon,normal_cut_ratio):
    return normal_price * (1-normal_cut_ratio) - normal_coupon
#（利润，固定成本，扣点成本）  到手价
def cal_real_price(profit,fix_cost,real_cut_ratio):
    return (profit + fix_cost)/(1 - real_cut_ratio)


#一口价
def cal_normal_price(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon):
    val=cal_real_price(profit,fix_cost,real_cut_ratio)
    return real_to_normal(val,normal_coupon,normal_cut_ratio)

#定价
def cal_org_price(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon,org_discont):
    val=cal_normal_price(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon)
    return normal_to_org(val,org_discont)




if __name__=="__main__":


    #一口价->定价
    normal_price=10000
    org_discont=0.9
    org_price=normal_to_org(normal_price,org_discont)
    print("一口价：{}，折扣：{}，定价：{}".format(normal_price,org_discont,org_price))

    #定价->一口价
    org_price=12000
    org_discont=0.9
    normal_price=org_to_normal(org_price,org_discont)
    print("定价：{}，折扣：{}，一口价：{}".format(org_price,org_discont,normal_price))

    #一口价->到手价
    real_price=15000
    normal_cut_ratio=0.05
    normal_coupon=1000
    normal_price=real_to_normal(real_price,normal_cut_ratio,normal_coupon)
    print("一口价：{}，折扣率：{}，优惠券：{}，到手价：{}".format(real_price,normal_cut_ratio,normal_coupon,normal_price))

    #到手价->一口价
    normal_price=12000
    normal_coupon=1000
    normal_cut_ratio=0.05
    real_price=normal_to_real(normal_price,normal_coupon,normal_cut_ratio)
    print("到手价：{}，折扣率：{}，优惠券：{}，一口价：{}".format(normal_price,normal_cut_ratio,normal_coupon,real_price))

    #利润，固定成本，扣点成本
    profit=10000
    fix_cost=5000
    real_cut_ratio=0.05
    normal_cut_ratio=0.05
    normal_coupon=1000
    normal_price=cal_normal_price(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon)
    print("利润：{}，固定成本：{}，扣点成本：{}，折扣率：{}，优惠券：{}，定价：{}".format(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon,normal_price))

    #定价
    profit=10000
    fix_cost=5000
    real_cut_ratio=0.05
    normal_cut_ratio=0.05
    normal_coupon=1000
    org_discont=0.9
    org_price=cal_org_price(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon,org_discont)
    print("利润：{}，固定成本：{}，扣点成本：{}，折扣率：{}，优惠券：{}，折扣：{}，定价：{}".format(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon,org_discont,org_price)) 