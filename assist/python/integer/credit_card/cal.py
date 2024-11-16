import datetime
from dateutil.relativedelta import relativedelta
import calendar


def get_date(year,month,day):
    
    year+= (month-1)//12
    month = (month-1)%12+1
    _, num_days = calendar.monthrange(year, month)
    return datetime.date(year,month,day if day>0 and day<=num_days else num_days)

def check_date(cur_date:datetime.date,day):
    _, num_days = calendar.monthrange(cur_date.year, cur_date.month)
    if day>0 and day<=num_days:
        return datetime.date(cur_date.year, cur_date.month,day)
    else:
        return cur_date
    
    
#billing_day：单天消费，计入下一周期
def calculate_days_to_repayment(current_date, billing_day, repayment_day):
    # 获取当前月份和年份
    current_month = current_date.month
    current_year = current_date.year
    
    try:
        # 计算本期账单日
        if current_date.day < billing_day:
            billing_date = get_date(current_year, current_month, billing_day)
        else:
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1
            billing_date = get_date(current_year, current_month, billing_day)
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
        return days_until_repayment,current_date,billing_date, repayment_date, billing_day, repayment_day
    except Exception as e:
        return 0

def month_add(current_date: datetime.date, offset=1):
    if offset > 0:
        return current_date + relativedelta(months=offset)
    elif offset < 0:
        return current_date - relativedelta(months=-offset)
    else:
        return current_date
    
def day_add(current_date: datetime.date, offset=1):
    if offset > 0:
        return current_date + datetime.timedelta(days=offset)
    elif offset < 0:
        return current_date - datetime.timedelta(days=-offset)
    else:
        return current_date

if __name__ == '__main__':
    
    
    # for i in range(-32,30):
    #     print(i,get_date(2023,i,31))

    bi_pay_days=[
    (24,18),
    (13,2),
    (18,7),
    (18,6),
    (18,8),
    (5,30),
    (9,27),
    (21,10),
    (28,22),
    (17,6),
    (7,25),
    (3,23),
    (4,24),
    ]



    lst=[]
    current_date=datetime.date(2023,12,1)
    for i in range(1,60):
        dest_date=day_add(current_date,i)
        for bi_day,pay_day in bi_pay_days:
            rest_days,date,billing_date, repayment_date, billing_day, repayment_day = calculate_days_to_repayment(dest_date, bi_day, pay_day)
            dic={
                "rest_days":rest_days,
                "current_date":date,
                "billing_date":billing_date,
                "repayment_date":repayment_date,
                "billing_day":billing_day,
                "repayment_day":repayment_day,

            }
            
            lst.append(dic)
    import pandas  as pd
    df=pd.DataFrame(lst)
    df.to_excel("pay_rest_days.xlsx")

