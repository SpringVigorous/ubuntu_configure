#一口价->定价
def normal_to_org(normal_price,discont):
    return normal_price / discont
#定价->一口价
def org_to_normal(org_price,discont):
    return org_price * discont  
#到手价->一口价
def real_to_normal(real_price,sub_ratio,sub_coupon):
    return (real_price +sub_coupon ) / (1-sub_ratio)

#一口价->到手价
def normal_to_real(normal_price,sub_coupon,sub_ratio):
    return normal_price * (1-sub_ratio) - sub_coupon
#（利润，固定成本，扣点成本）  到手价
def cal_real_price(profit,fix_cost,radio_cost):
    return (profit + fix_cost)/(1 - radio_cost)


#一口价
def cal_normal_price(profit,fix_cost,radio_cost,sub_ratio,sub_coupon):
    val=cal_real_price(profit,fix_cost,radio_cost)
    return real_to_normal(val,sub_coupon,sub_ratio)

#定价
def cal_org_price(profit,fix_cost,radio_cost,sub_ratio,sub_coupon,discont):
    val=cal_normal_price(profit,fix_cost,radio_cost,sub_ratio,sub_coupon)
    return normal_to_org(val,discont)


if __name__=="__main__":
    #一口价->定价
    normal_price=10000
    discont=0.9
    org_price=normal_to_org(normal_price,discont)
    print("一口价：{}，折扣：{}，定价：{}".format(normal_price,discont,org_price))

    #定价->一口价
    org_price=12000
    discont=0.9
    normal_price=org_to_normal(org_price,discont)
    print("定价：{}，折扣：{}，一口价：{}".format(org_price,discont,normal_price))

    #一口价->到手价
    real_price=15000
    sub_ratio=0.05
    sub_coupon=1000
    normal_price=real_to_normal(real_price,sub_ratio,sub_coupon)
    print("一口价：{}，折扣率：{}，优惠券：{}，到手价：{}".format(real_price,sub_ratio,sub_coupon,normal_price))

    #到手价->一口价
    normal_price=12000
    sub_coupon=1000
    sub_ratio=0.05
    real_price=normal_to_real(normal_price,sub_coupon,sub_ratio)
    print("到手价：{}，折扣率：{}，优惠券：{}，一口价：{}".format(normal_price,sub_ratio,sub_coupon,real_price))

    #利润，固定成本，扣点成本
    profit=10000
    fix_cost=5000
    radio_cost=0.05
    sub_ratio=0.05
    sub_coupon=1000
    normal_price=cal_normal_price(profit,fix_cost,radio_cost,sub_ratio,sub_coupon)
    print("利润：{}，固定成本：{}，扣点成本：{}，折扣率：{}，优惠券：{}，定价：{}".format(profit,fix_cost,radio_cost,sub_ratio,sub_coupon,normal_price))

    #定价
    profit=10000
    fix_cost=5000
    radio_cost=0.05
    sub_ratio=0.05
    sub_coupon=1000
    discont=0.9
    org_price=cal_org_price(profit,fix_cost,radio_cost,sub_ratio,sub_coupon,discont)
    print("利润：{}，固定成本：{}，扣点成本：{}，折扣率：{}，优惠券：{}，折扣：{}，定价：{}".format(profit,fix_cost,radio_cost,sub_ratio,sub_coupon,discont,org_price)) 






