

import datetime





def repay_days_rest(current_date, repayment_day, billing_day, is_billing_day_included=False):
    # 获取当前月份和年份
    current_month = current_date.month
    current_year = current_date.year
    
    
    try:
        # 计算账单日
        billing_date = datetime.date(current_year, current_month, billing_day)
        
        # 如果当前日期已经过了账单日，则账单日在下个月
        if current_date > billing_date:
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1

            billing_date = datetime.date(current_year, current_month, billing_day)
        
        next_month =1 if  repayment_day< billing_day else 0
        # 计算还款日
        repayment_date = datetime.date(current_year, billing_date.month+next_month, repayment_day)


        # 计算距离还款日的天数
        days_until_repayment = (repayment_date - current_date).days
        
        # 如果账单日当天的消费计入当前周期，需要调整计算逻辑
        if is_billing_day_included and current_date >= billing_date:
            days_until_repayment -= 1
        return days_until_repayment
    except Exception as e:
        return 0



if __name__ == '__main__':
    current_date = datetime.datetime.now().date()
    repayment_day = 15
    billing_day = 10
    is_billing_day_included = True
    
    days_until_repayment = repay_days_rest(current_date, repayment_day, billing_day, is_billing_day_included)
    
    print(days_until_repayment)