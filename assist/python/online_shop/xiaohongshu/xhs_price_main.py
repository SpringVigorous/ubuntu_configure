import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../..")))
from price_calculator import PriceCalculator

from price_config import *
# from calcluate_tools import *
from base.math_tools import *

def cal_fix_cost(product_price, box_unit_count, deliver_unit_count,box_info,bill_info,cut_ratio,profit):
    # 进行第一次交叉连接

    box_cost=product_price*box_unit_count+box_info[0]
    deliver_cost=box_cost*deliver_unit_count+bill_info[0]
    # return cal_real_price(profit,deliver_cost,cut_ratio)
    return deliver_cost

def cal_weight(product_wight, box_unit_count, deliver_unit_count,box_info,bill_info):
    # 进行第一次交叉连接
    product_wight, box_unit_count, deliver_unit_count
    box_cost=product_wight*box_unit_count+box_info[1]
    deliver_cost=box_cost*deliver_unit_count+bill_info[1]
    return deliver_cost/1000.0


    
config=TeaConfig(r"E:\花茶\价格")
result_dir=os.path.join(config.src_dir,"结果")
os.makedirs(result_dir,exist_ok=True)
product_path= os.path.join(result_dir, "产品规格.xlsx")

def ratio_val(df, col_name,val,dest_name,default_val):
    try:
        results= df.loc[df[col_name] == val, dest_name]
        if result.empty:
            return default_val
        return results[-1]
    except:
        return default_val
    
    
    
def product_df():
    if os.path.exists(product_path):
        return pd.read_excel(product_path,sheet_name="规格")
            
    product_price=config.product_prices_df.copy()
    box_unit_price=config.box_unit_df.copy()
    deliver_unit_price=config.deliver_unit_df.copy()

    # 添加临时常量列
    product_price['key'] = 1
    box_unit_price['key'] = 1
    deliver_unit_price['key'] = 1

    # 进行第一次交叉连接
    result1 = pd.merge(product_price, box_unit_price, on='key')
    # 进行第二次交叉连接
    result = pd.merge(result1, deliver_unit_price, on='key').drop('key', axis=1)
    # 检查是否有未命名的列，并重命名
    if 'Unnamed: 0' in result.columns:
        result.rename(columns={'Unnamed: 0': '产品规格'}, inplace=True)
    result["利润"]=5
    result["优惠"]=config.get_normal_discount()
    result["一口价折扣比率"]=config.normal_cut_radio
    result["定价折扣"]=config.org_rebate
    result["产品规格"]=result.apply(lambda x: f"{x['产品']}-{x['小包数']}包-{x['盒数']}盒", axis=1)
    # result["快递费"]=result.apply(lambda x: x['单包总价']*config.express_ratio, axis=1)
    ratio_df=config.fix_cut_ratio
    

    
    result["提现费率"]=ratio_val(ratio_df,"名称",'提现费率', '比率',.005)
    result["运费险"]=1.5

    # result["物料费"]=0
    result["快递费"]=8
    result["平台券"]=0
    result["商家券"]=5
    result["佣金比率"]=ratio_val(ratio_df,"名称",'佣金比率', '比率',.01)
    
    os.makedirs(os.path.dirname(product_path), exist_ok=True)
    result.to_excel(product_path,sheet_name="规格",index=False)
    


    
    
    
    return result
    




if __name__=="__main__":
    df=product_df()

    result=df.copy()
    
    result["物料费"]=result.apply(lambda x: cal_fix_cost(x['单包总价'],x['小包数'],x['盒数'],
                                                      config.fix_box_info,config.fix_bill_info,config.fix_cut_ratio,x['利润']), axis=1)

    def cal_fun(row):
        calculator= PriceCalculator(row["物料费"],
            row["快递费"],
            row["商家券"],
            row["平台券"],
            row["提现费率"],
            row["运费险"],
            row["一口价折扣比率"],
            row["佣金比率"],
            row["定价折扣"],)
        
        calculator.calculate_by_profit(row["利润"])
        val=ceil_5(calculator.result("一口价"))
        dic=calculator.calculate_by_normal_price(val)
        key="产品规格"
        dic[key]=row[key]
        return pd.Series(dic)
    
    datas=result.apply(cal_fun, axis=1)
    result["总质量(kg)"]=result.apply(lambda x:cal_weight(x['单包总质量'],x['小包数'],x['盒数'],
                                                      config.fix_box_info,config.fix_bill_info), axis=1)
    
    with pd.ExcelWriter(os.path.join(result_dir, "推荐定价.xlsx"),engine="xlsxwriter") as writer:
        result.to_excel(writer,sheet_name="成本设置",index=False)
        datas.to_excel(writer,sheet_name="推荐定价",index=False)

    
    
    
    
    
    
    
    
    
    