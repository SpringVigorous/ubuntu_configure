

import datetime
from dateutil.relativedelta import relativedelta
import calendar

#返回日期，内部自动对 month,day进行修正处理
#month 小于1 或者大于12 则自动修正为1-12
"""eg: 
    2021/0/31 -> 2020/12/31
    2021/18/31 -> 2022/6/30
    2021/-10/31 -> 2020/2/29
    2011/24/31 -> 2012/12/31
"""
def get_date(year,month,day):
    year+= (month-1)//12
    month = (month-1)%12+1
    _, num_days = calendar.monthrange(year, month)
    return datetime.date(year,month,day if day>0 and day<=num_days else num_days)

#日期不小于指定的day 
def date_noless_by_day(current_date, day):
    # 获取当前月份和年份
    current_month = current_date.month
    current_year = current_date.year
    if current_date.day > day:
        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1
    return get_date(current_year, current_month, day)


#当天距离当前周期还款日的 剩余天数
def cur_cycle_to_paydays(current_date, repayment_day):
    # 获取当前月份和年份
    if  repayment_day<1:
        return 0
    
    try:
        # 计算还款日
        repayment_date = date_noless_by_day(current_date, repayment_day)

        # 计算距离还款日的天数
        days_until_repayment = (repayment_date - current_date).days

        return days_until_repayment
    except Exception as e:
        return 0
    
def day_add(current_date: datetime.date, offset=1):
    if offset > 0:
        return current_date + datetime.timedelta(days=offset)
    elif offset < 0:
        return current_date - datetime.timedelta(days=-offset)
    else:
        return current_date
def month_add(current_date: datetime.date,offset=1):
    if offset>0:
        return current_date + relativedelta(months=offset)
    elif offset<0:
        return current_date - relativedelta(months=-offset)
    else:
        return current_date


def get_days_in_month(year, month):
    _, num_days = calendar.monthrange(year, month)
    return num_days




def check_date(cur_date:datetime.date,day):
    _, num_days = calendar.monthrange(cur_date.year, cur_date.month)
    if day>0 and day<=num_days:
        return datetime.date(cur_date.year, cur_date.month,day)
    else:
        return cur_date
    

#当天消费距离下一周期还款日的 剩余天数
def cur_consume_to_paydays(current_date, billing_day, repayment_day):
    
    if billing_day<1 or repayment_day<1:
        return 0
    
    try:
        # 计算本期账单日

        billing_date = date_noless_by_day(current_date, billing_day)
        # 判断账单日和还款日的关系
        if billing_day <= repayment_day:
            # 账单日小于还款日，还款日为账单日所在月份
            repayment_date = get_date(billing_date.year, billing_date.month, repayment_day)
        else:
            # 账单日大于或等于还款日，还款日为下一期的账单日
            next_month = month_add(billing_date, 1)
            repayment_date = get_date(next_month.year, next_month.month, repayment_day)
        
        # 计算距离还款日的天数
        days_until_repayment = (repayment_date - current_date).days
        
        # return days_until_repayment,current_date,billing_date, repayment_date, billing_day, repayment_day
        return days_until_repayment
    except Exception as e:
        return 0


if __name__ == '__main__':
    current_date = datetime.datetime.now().date()
    print(get_date(2021,0,31))
    print(get_date(2021,18,31))
    print(get_date(2021,-10,31))
    print(get_date(2011,24,31))


    exit(0)
    
    next_month=month_add(current_date,5)
    next_month=month_add(next_month,-8)
    
    repayment_day = 1
    billing_day = 13
    is_billing_day_included = True
    
    days_until_repayment = cur_consume_to_paydays(current_date, repayment_day, billing_day, is_billing_day_included)
    
    print(days_until_repayment)