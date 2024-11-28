import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from price_config import *
from calcluate_tools import *


def cal_fix_cost(product_price, box_unit_count, deliver_unit_count,box_info,bill_info,cut_ratio,profit):
    # 进行第一次交叉连接

    box_cost=product_price*box_unit_count+box_info[0]
    deliver_cost=box_cost*deliver_unit_count+bill_info[0]
    return cal_real_price(profit,deliver_cost,cut_ratio)

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
    result["每满减折扣"]=config.normal_cut_radio
    result["定价折扣"]=config.org_rebate
    result["产品规格"]=result.apply(lambda x: f"{x['产品']}-{x['小包数']}包-{x['盒数']}盒", axis=1)
    # result["快递费"]=result.apply(lambda x: x['单包总价']*config.express_ratio, axis=1)
    
    os.makedirs(os.path.dirname(product_path), exist_ok=True)

    result.to_excel(product_path,sheet_name="规格",index=False)
    
    
    return result
    




if __name__=="__main__":
    result=product_df()
    
    # result["单盒费用"]
    
    # result["单盒费用"]
    
    
    result["成本价"]=result.apply(lambda x: cal_fix_cost(x['单包总价'],x['小包数'],x['盒数'],
                                                      config.fix_box_info,config.fix_bill_info,config.fix_cut_ratio,x['利润']), axis=1)
    result["一口价"]=result.apply(lambda x: real_to_normal(x["成本价"],x["每满减折扣"],x["优惠"]), axis=1)
    result["定价"]=result.apply(lambda x: normal_to_org(x['一口价'],x["定价折扣"]), axis=1)
    

    result["总质量(kg)"]=result.apply(lambda x:cal_weight(x['单包总质量'],x['小包数'],x['盒数'],
                                                      config.fix_box_info,config.fix_bill_info), axis=1)

    result.to_excel(os.path.join(result_dir, "result.xlsx"))
    
    
    
    
    
    
    
    
    
    