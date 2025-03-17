import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../..")))
from price_calculator import PriceCalculator

from price_config import *
# from calcluate_tools import *
from base.math_tools import *
from base.df_tools import find_last_value_by_col_val
from base import clear_folder,sheet_names
def cal_fix_cost(product_price, box_unit_count, deliver_unit_count,box_info,bill_info):
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

pay_ratio_name="服务费率（佣金+支付渠道+...）"





def check_df(df):
    if df is None:
        return False
    if df.empty:
        return False
    return True

def product_df(config:TeaConfig,product_path):
    # 定义规格和预设参数的sheet名称
    pre_unit_name="预设规格"
    unit_name="规格"
    preset_name="预设价格"
    names=sheet_names(product_path)
    # 检查产品路径是否存在
    pre_unit_df=None
    product_unit_df =None
    product_preset_df=None
    if unit_name in names or preset_name in names:
        with pd.ExcelFile(product_path) as reader:
            if pre_unit_name in names:
                pre_unit_df = reader.parse(pre_unit_name)
            if unit_name in names:
                product_unit_df = reader.parse(unit_name)
            if preset_name in names:
                product_preset_df = reader.parse(preset_name)
    if check_df(product_preset_df):
        return product_preset_df            
    

    
   #产品小包价格信息表
    product_price=config.product_prices_df.copy()
    
    if not check_df(pre_unit_df):
        box_unit_price=config.box_unit_df.copy()
        deliver_unit_price=config.deliver_unit_df.copy()
        # 添加临时常量列
        product_price['key'] = 1
        box_unit_price['key'] = 1
        deliver_unit_price['key'] = 1
        # 进行第一次交叉连接 盒-小包数
        result1 = pd.merge(deliver_unit_price, box_unit_price, on='key')
        # 进行第二次交叉连接 产品-盒-小包数
        result = pd.merge(product_price,result1,  on='key').drop('key', axis=1)
        result["产品规格"]=result.apply(lambda x: f"{x['产品']}-{x['小包数']}包-{x['盒数']}盒", axis=1)

        pre_unit_df=result[["产品规格","产品","小包数","盒数"]]

    if not check_df(product_unit_df):
        result=pd.merge(pre_unit_df,product_price,on=["产品"])
        result["物料费"]=result.apply(lambda x: cal_fix_cost(x['单包总价'],x['小包数'],x['盒数'],
                                                        config.fix_box_info,config.fix_bill_info,), axis=1)
        
        result["物料重"]=result.apply(lambda x: cal_weight(x['单包总重'],x['小包数'],x['盒数'],
                                                        config.fix_box_info,config.fix_bill_info,), axis=1)
        product_unit_df=result[["产品规格","物料费","物料重"]]

    product_preset_df=product_unit_df.copy()     
    product_preset_df["定价"]=100
    product_preset_df["利润"]=5
    product_preset_df["优惠"]=config.get_normal_discount()
    product_preset_df["满减折扣比率"]=config.normal_cut_radio

    # product_preset_df["快递费"]=product_preset_df.apply(lambda x: x['单包总价']*config.express_ratio, axis=1)
    ratio_df=config.reduce_ratio_df

    product_preset_df["提现费率"]=find_last_value_by_col_val(ratio_df,"名称",'提现费率', '比率',.005)
    product_preset_df["运费险"]=1.5
    product_preset_df["快递费"]=5.3
    product_preset_df["平台券"]=0
    product_preset_df["商家券"]=0
    
    pay_radio_lst=[find_last_value_by_col_val(ratio_df,"名称",'佣金比率', '比率',.03),
               find_last_value_by_col_val(ratio_df,"名称",'支付渠道费', '比率',.03),
            #    find_last_value_by_col_val(ratio_df,"名称",'信用卡分期', '比率',.03),
               ]
        
    product_preset_df[pay_ratio_name]=sum(filter(lambda x: x is not None, pay_radio_lst))
    
    #删除不需要的列

    os.makedirs(os.path.dirname(product_path), exist_ok=True)
    
    with pd.ExcelWriter(product_path) as writer:
        pre_unit_df.to_excel(writer,sheet_name=pre_unit_name,index=False)
        product_unit_df.to_excel(writer,sheet_name=unit_name,index=False)
        product_preset_df.to_excel(writer,sheet_name=preset_name,index=False)
    return product_preset_df
    




if __name__=="__main__":
    config=TeaConfig(r"E:\花茶\价格","详情")
    result_dir=os.path.join(config.src_dir,"结果","小红书")
    os.makedirs(result_dir,exist_ok=True)
    product_path= os.path.join(result_dir,"产品规格-计算.xlsx")
    
    #清除所有中间结果，重新计算
    #单包产品药材费
    # clear_folder(config.sub_dir_path)
    #规格费用
    # clear_folder(result_dir)
    
    config.init_data()
    # 获取 结果/小红书/产品规格.xlsx
    df=product_df(config,product_path)

    result=df.copy()
    
    # result["物料费"]=result.apply(lambda x: cal_fix_cost(x['单包总价'],x['小包数'],x['盒数'],
    #                                                   config.fix_box_info,config.fix_bill_info,), axis=1)

    recursive_dict=[]
    show_recursive=True
    flag:str=None
    def cal_fun(row):
        
        
        
        calculator= PriceCalculator(row["物料费"],
            row["快递费"],
            row["商家券"],
            row["平台券"],
            row["提现费率"],
            row["运费险"],
            row["满减折扣比率"],
            row[pay_ratio_name],)
        #利润率计算
        
        # calculator.calculate_by_normal_price(28.8)
        # calculator.calculate_by_normal_price(row["定价"])
        calculator.calculate_by_profit_ratio(.01)
        #利润率
        # calculator.calculate_by_gross_profit_ratio(.6)
        # calculator.calculate_by_profit(row["利润"])


        global recursive_dict
        global flag
        flag=calculator.flag_type
        key="产品规格"
        dic={key:row[key]}
        #查看递归过程
        if show_recursive:
            recursive_dict.extend(calculator.recursive_info(key,row[key]))  
        
        
        #取整后，重新定价
        normal_price=ceil_5(calculator.result("定价"))
        dic.update(calculator.calculate_by_normal_price(normal_price))
        return pd.Series(dic)
    
    datas=result.apply(cal_fun, axis=1)

    
    with pd.ExcelWriter(os.path.join(result_dir, f"推荐定价_{flag}.xlsx"),engine="xlsxwriter") as writer:
        result.to_excel(writer,sheet_name="固定成本",index=False)
        datas.to_excel(writer,sheet_name=f"推荐定价-详情",index=False)
        datas.to_excel(writer,sheet_name=f"推荐定价",index=False)
        
        
        if show_recursive:
            pd.DataFrame(recursive_dict).to_excel(writer,sheet_name="递归过程",index=False)

    
    
    
    
    
    
    
    
    
    