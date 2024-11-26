#org_discont:定价折扣（8折扣->.8);k
#org_price:定价;a
#normal_price:一口价;b
#real_price:到手价;c
#normal_cut_ratio:一口价折扣比率（8折扣->.2);j
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


#org_discont:定价折扣（8折扣->.8);k
#org_price:定价;a
#normal_price:一口价;b
#real_price:到手价;c
#normal_cut_ratio:一口价折扣比率（8折扣->.2);j
#normal_coupon:优惠券金额;i
#profit:利润;d
#fix_cost:固定成本;f
#real_cut_ratio:到手价扣点比率，浮动成本率;h
#brokerage_cut_ratio:佣金比例（基数：一口价);l
#brokerage_cut:佣金;m
#real_cut_cost:到手价扣点成本;g
#final_cost:最终成本;e





class PriceCalculator:
    
    #profit:利润;d
    #fix_cost:固定成本;f
    #real_cut_ratio:到手价扣点比率，浮动成本率;h
    #normal_cut_ratio:一口价折扣比率（8折扣->.2);j
    #normal_coupon:优惠券金额;i
    #brokerage_cut_ratio:佣金比例（基数：一口价);l
    #org_discont:定价折扣（8折扣->.8);k
    def __init__(self,profit:float,fix_cost:float,real_cut_ratio:float=.2,normal_cut_ratio:float=.05,normal_coupon:float=20,brokerage_cut_ratio:float=.1,org_discont:float=.9):
        self.reset(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon,brokerage_cut_ratio,org_discont)

    def reset(self,profit:float,fix_cost:float,real_cut_ratio:float=.2,normal_cut_ratio:float=.05,normal_coupon:float=20,brokerage_cut_ratio:float=.1,org_discont:float=.9):
                #定价折扣 八折->.8
        self.org_discont:float=org_discont
        #一口价固定券
        self.normal_coupon:float=normal_coupon
        #一口价折扣率
        self.normal_cut_ratio:float=normal_cut_ratio

        #佣金比例(基数是一口价)
        self.brokerage_cut_ratio:float=brokerage_cut_ratio
        #利润
        self.profit:float=profit
        #固定成本
        self.fix_cost:float=fix_cost
        #扣点比率
        self.real_cut_ratio:float=real_cut_ratio
    #real_cut_cost:到手价扣点成本;g
    @property
    def real_cut_cost(self):
        return self.real_price*self.real_cut_ratio
    #final_cost:最终成本;e
    #成本
    @property
    def final_cost(self):
        return self.fix_cost+self.real_cut_cost+self.brokerage_cut

    #brokerage_cut:佣金;m
    @property
    def brokerage_cut(self):
        return self.brokerage_cut_ratio*self.normal_price

    #normal_price:一口价;b
    @property
    def normal_price(self):
        return (self.normal_coupon*(self.real_cut_ratio-1)-self.profit-self.fix_cost)/((1-self.normal_cut_ratio)*(self.real_cut_ratio-1)+self.brokerage_cut_ratio)
        

    #real_price:到手价;c
    @property
    def real_price(self):
        return -((1-self.normal_cut_ratio)*(self.profit+self.fix_cost)+self.brokerage_cut_ratio*self.normal_coupon)/((self.real_cut_ratio-1)*(1-self.normal_cut_ratio)+self.brokerage_cut_ratio)

    #org_price:定价;a
    @property
    def org_price(self):
        return self.normal_price/self.org_discont
    
    #通过原始定价：计算净利润
    def cal_profit_by_org_price(self,org_price):
        normal_price=org_price*self.org_discont
        return self.cal_profit_by_normal_price(normal_price)

    #通过一口价：计算净利润
    def cal_profit_by_normal_price(self,normal_price):
        real_price=normal_price*(1-self.normal_cut_ratio)-self.normal_coupon
        return self.cal_profit_by_real_price(real_price)

    #通过到手价：计算净利润
    def cal_profit_by_real_price(self,real_price):
        norm_price=(real_price+self.normal_coupon)/(1-self.normal_cut_ratio)
        val= real_price*(1-self.real_cut_ratio)-norm_price*self.brokerage_cut_ratio-self.fix_cost
        self.profit=val
        
        return val

    def info(self):
        print("定价：{},折扣率：{}".format(self.org_price,self.org_discont))
        print("一口价：{},折扣率：{},优惠券：{}".format(self.normal_price,self.normal_cut_ratio,self.normal_coupon))
        print("到手价：{}".format(self.real_price))
        print("固定成本：{}".format(self.fix_cost))
        print("佣金：{},佣金比率：{}".format(self.brokerage_cut,self.brokerage_cut_ratio))
        print("扣点成本{},扣点比率：{}".format(self.real_cut_cost,self.real_cut_ratio))
        print("最终成本：{}".format(self.final_cost))
        print("利润：{}".format(self.profit))

if __name__=="__main__":
    profit=5
    fix_cost=20
    real_cut_ratio=.25
    normal_cut_ratio=0
    normal_coupon=20
    brokerage_cut_ratio=.3
    org_discont=.8

    calculator=PriceCalculator(profit,fix_cost,real_cut_ratio,normal_cut_ratio,normal_coupon,brokerage_cut_ratio,org_discont)
    calculator.info()
    print("-"*30)
    calculator.cal_profit_by_org_price(110)
    calculator.info()
    
    
    exit(0)
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