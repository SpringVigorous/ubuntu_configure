import numpy as np
import matplotlib.pyplot as plt
def binary_caluclate(cal_fun,compare_fun,min_val,max_val,tolence,val,*kargs):
    

    mid_val = (min_val+max_val)/2

    while not compare_fun(min_val,max_val,tolence):
        mid_val = (min_val+max_val)/2
    
        mid_temp = cal_fun(mid_val,*kargs)
        
        if compare_fun(mid_temp,val,tolence):
            break
        elif mid_temp<val:
            min_val=mid_val
        else:
            max_val=mid_val
    return mid_val
# 计算相对误差: 结果值、期望值、容忍度（误差值/较大值）
def relative_rate_zero(result,desire,tolence):
    # val=abs(result-desire)/max(abs(result),abs(desire))
    val=abs(result-desire)/abs(desire)
    return  val<=tolence


#单利计算的月供比例
def simple_month_pay_rate(year_rate, periods):
    q=year_rate/12
    n=periods
    return (q*n+1)/(n*(1+(n-1)/2.0*q))
    
#复利计算的月供比例（房贷）
def compound_month_pay_rate(year_rate, periods):
    q=year_rate/12
    n=periods
    product_radio=(1+q)**n
    b=(q*product_radio)/(product_radio-1) #月供/本金
    return b
    
#信用卡分期计算的月供比例
def stage_month_pay_rate(year_rate, periods):
    q=year_rate/12
    n=periods
    return q+1.0/n

# 信用卡分期(直接一次性付完所有利息),月供占真实本金的比例
def stage_month_pre_pay_rate(year_rate,periods):
    q=year_rate/12
    n=periods
    return 1/((1-n*q)*n)


#单利计算的年利率 -根据月供比例换算
def simple_annual_rate(month_pay_rate, periods):
    y=month_pay_rate
    n=periods
    
    
    return (n*y-1)/(n*(1-(n-1)*y/2.0))*12
    
    # return 12.0/(n*(1+(n-1)/2.0*month_pay_rate-1))
#复利计算的年利率 -根据月供比例换算（房贷）
def compound_annual_rate(month_pay_rate, periods):

    min_month_pay_rate = .001
    max_month_pay_rate = 1.2
    tolence=1e-6
      
    val=binary_caluclate(compound_month_pay_rate,relative_rate_zero,min_month_pay_rate,max_month_pay_rate,tolence,month_pay_rate,periods)
    
    return val
    
#信用卡分期计算的年利率 -根据月供比例换算
def stage_annual_rate(month_pay_rate, periods):
    n=periods
    return (month_pay_rate-1.0/n)*12






 

# 计算等额月供情况下的名义年利率，房贷等额本息->个人信用卡分期
#real_monthly_rate： 月利率
#periods： 期数（月数）
#return : 年利率
def calculate_annual_year_rate(real_year_rate, periods):
    q=real_year_rate/12
    n=periods
    product_radio=(1+q)**n
    b=(q*product_radio)/(product_radio-1) #月供/本金
    val=(b-1.0/n)*12

    return val




#年利率:信用卡分期 -> 房贷等额本息
def convert_stage_to_compound(year_rate, periods):
    month_pay_rate=stage_month_pay_rate(year_rate,periods)
    return compound_annual_rate(month_pay_rate,periods)

#年利率:信用卡分期(一次性结清所有利息) -> 房贷等额本息
def convert_pre_stage_to_compound(year_rate, periods):
    pay_rate=stage_month_pre_pay_rate(year_rate,periods)
    
    return compound_annual_rate(pay_rate,periods)

    
#年利率:房贷等额本息 ->信用卡分期 
def convert_compound_to_stage(year_rate, periods):
    month_pay_rate=compound_month_pay_rate(year_rate,periods)
    return stage_annual_rate(month_pay_rate,periods)

#年利率：信用卡分期 -> 单利
def convert_stage_to_simple(year_rate, periods):
    month_pay_rate=stage_month_pay_rate(year_rate,periods)
    return simple_annual_rate(month_pay_rate,periods)

#年利率:单利 -> 信用卡分期
def convert_simple_to_stage(year_rate, periods):
    month_pay_rate=simple_month_pay_rate(year_rate,periods) 
    return stage_annual_rate(month_pay_rate,periods)

#年利率:房贷等额本息 ->单利
def convert_compound_to_simple(year_rate, periods):
    month_pay_rate=compound_month_pay_rate(year_rate,periods)
    return simple_annual_rate(month_pay_rate,periods)

#年利率：单利 -> 房贷等额本息
def convert_simple_to_compound(year_rate, periods):
    month_pay_rate=simple_month_pay_rate(year_rate,periods) 
    return compound_annual_rate(month_pay_rate,periods)


def plot_test():
    import matplotlib.pyplot as plt
    def figure_spin_rate(x, y,flag, color='blue'):


        # 绘制点状线
        plt.plot(x, y, 'o-', color=color, label=f'Annual Rate: {flag}')
        # 绘制最大点
        max_y=max(y)
        max_index=y.index(max(y))
        max_x=x[max_index]
        max_color="black"
        
        plt.plot(max_x, max_y, 'o', color=max_color)
        # 绘制最大值
        plt.text(max_x, max_y, f'{max_x}\n {max_y:.2%}', ha='center', va='bottom', color=max_color)
        for i in x:
            pos='bottom' if i %2 == 0 else  'top'
            plt.text(i, y[x.index(i)], f'{i}\n {y[x.index(i)]:.2%}', ha='center', va=pos, color=color)
        
        
    plt.xlabel('Periods')
    plt.ylabel('Compound Value')
    plt.title('Compound Interest Over Time')
    plt.grid(True)


    periods=60
    x=list(range(1, periods + 1))
    rates=[(0.03,"red"),
            (0.05,"blue"),
            (0.06,"green")]

    # 调用函数，固定 annual_rate 为 0.03，periods 从 12 到 360  
    y=[[convert_stage_to_compound(annual_rate,period)for period in range(1, periods + 1) ] for annual_rate,_ in rates]
    
    xy=list(zip(x,*y))
    vals="\n".join( ["\t".join(  map(str,items))  for items in xy])
    with open("pay_rate.txt","w") as f:
        f.write(vals)
    
    for val,rate in   zip(y,rates):
        figure_spin_rate(x,val,str(rate[0]),color=rate[1])
    
    
    plt.legend()
    plt.show()
    
    


if __name__=="__main__":


    # plot_test()
        
    annual_rate=.03
    periods=60


    # pay_rate=stage_month_pre_pay_rate(annual_rate,periods)
    
    # val=compound_annual_rate(pay_rate,periods)
    
    
    # a=compound_month_pay_rate(val,periods)


    # print(val,a)
    print(convert_pre_stage_to_compound(annual_rate,periods))
    # # print(convert_stage_to_compound(annual_rate,periods))
    # print(convert_stage_to_simple(annual_rate,periods))


