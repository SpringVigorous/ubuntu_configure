import os
import pandas as pd 
import numpy as np 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.com_log import logger_helper
from base.df_tools import *
class TeaConfig:
    def __init__(self,org_dir=r"E:\花茶\价格",sub_dir="详情") -> None:
        self.src_dir=org_dir  # 设置源目录

        # 初始化配置类，设置初始目录和其他默认文件名
        self.src_dir=org_dir  # 设置源目录
        self.purchase_name="采购价格"
        self.usage_name="产品用量.xlsx"
        self.consume_name="额外费用.xlsx"
        self.cut_ratio_name="扣费比率.xlsx"
        self.discount_name="优惠活动.xlsx"
        self.sub_dir=sub_dir
        self.product_medical_name="产品药材价格"
        self.product_price_name="产品价格"
        self.medical_price_dict={}
        # self.init_data()
        
        pass
    @property
    def sub_dir_path(self):
        return os.path.join(self.src_dir,self.sub_dir)
        
        
        
    def medical_price(self,name):
        if self.medical_price_dict.get(name,None):
            return self.medical_price_dict.get(name)
        else:
            rows=find_values_by_col_val_contains(self.purchase_price_df,'产品',name,'单价').tolist()
            val= rows[0] if len(rows)>0 else 0.0
            self.medical_price_dict[name]=val
            return val
            
            

    def init_product(self):
        
        detail_path= self.product_price_path
        if os.path.exists(detail_path):
            try:
                self.product_prices_df = pd.read_excel(detail_path, sheet_name=self.product_price_name)
                return
            except:
                pass
        
        self.purchase_price_df = pd.read_excel(self.purchase_path, sheet_name='采购价格')
        self.purchase_price_df["单价"]=self.purchase_price_df["单价-kg"]/1000
        product_usage_df = pd.read_excel(self.usage_path, sheet_name='用量')
        
        # 将 medical_price 函数转换为向量化版本
        vectorized_medical_price = np.vectorize(self.medical_price)
        # 使用向量化操作计算“药材单价”
        product_usage_df["药材单价"] = vectorized_medical_price(product_usage_df['药材'])
        product_usage_df["单一药材总价"] = product_usage_df['药材单价']*product_usage_df["实际规格"]

        def cal_product_medical_price(group):
            # 计算每种药材的总价
            total_price = group["单一药材总价"].sum()
            # 计算每种药材的总质量
            total_weight = group["实际规格"].sum()
            
            # 返回一个包含总价格和总质量的 Series
            return pd.Series({
                "单包药材总价": total_price,
                "单包药材质量": total_weight
            })

        # 应用优化后的函数
        self.product_medical_prices_df = (
            product_usage_df
            .groupby(['产品'], sort=False)
            .apply(cal_product_medical_price,include_groups=False)
            .reset_index()
        )


        
        
        self.product_medical_prices_df["产品"].to_excel( os.path.join(self.src_dir,"产品名.xlsx"))
        
        
        #需要保留原始数据，可以将结果合并回去
        product_usage_df = product_usage_df.merge(
            self.product_medical_prices_df,
            on='产品',
            how='left'
        )
        # 计算产品总价
        self.product_prices_df=self.product_medical_prices_df.copy()
        self.product_prices_df["单包耗材单价"],self.product_prices_df["单包耗材质量"]=self.fix_pack_info
        self.product_prices_df["单包总价"]=self.product_prices_df["单包药材总价"]+self.product_prices_df["单包耗材单价"]
        self.product_prices_df["单包总质量"]=self.product_prices_df["单包药材质量"]+self.product_prices_df["单包耗材质量"]
        
        # product_prices=product_usage_df.groupby(['产品'],sort=False).apply(cal_product_price,include_groups=False).reset_index(name="总价")

        os.makedirs(os.path.dirname(detail_path), exist_ok=True)
        with pd.ExcelWriter(detail_path) as writer:
                self.purchase_price_df.to_excel(writer,sheet_name=self.purchase_name)
                self.product_medical_prices_df.to_excel(writer,sheet_name=self.product_medical_name)
                self.product_prices_df.to_excel(writer,sheet_name=self.product_price_name)
                product_usage_df.to_excel(writer,sheet_name="产品价格-详情")

    def get_normal_discount(self,price=0,quantity=0):
        return 5
        
    def init_data(self):
        
        with pd.ExcelFile(self.consume_path) as reader:
            # 读取 "单包" 表
            self.fix_pack_df = reader.parse('单包')
            self.fix_pack_info = (self.fix_pack_df['单价'].sum(),self.fix_pack_df['质量'].sum())
            
            # 读取 "单盒" 表
            self.fix_box_df = reader.parse('单盒')
            self.fix_box_info = (self.fix_box_df['单价'].sum(),self.fix_box_df['质量'].sum())
            
            # 读取 "单次" 表
            self.fix_bill_df = reader.parse('单次')
            self.fix_bill_info = (self.fix_bill_df['单价'].sum(),self.fix_bill_df['质量'].sum())
        
        

        self.reduce_ratio_df = pd.read_excel(self.cut_ratio_path, sheet_name='扣费比率')
        self.fix_cut_ratio = self.reduce_ratio_df['比率'].sum()
        
        with pd.ExcelFile(self.discount_path) as reader:
        
            self.each_discount_df = reader.parse('跨店满减')
            self.normal_discount_df = reader.parse('满减')
            
            normal_rebate_df= reader.parse('满减折扣')
            self.normal_cut_radio=1-normal_rebate_df.loc[0]["折扣"]


        with pd.ExcelFile(os.path.join(self.src_dir, "产品规格.xlsx")) as reader:
            self.box_unit_df=reader.parse("盒规格")
            self.deliver_unit_df=reader.parse("快递规格")
        self.init_product()
        pass
    @property
    def purchase_path(self):
        return os.path.join( self.src_dir , f"{self.purchase_name}.xlsx")
    @property
    def usage_path(self):
        return os.path.join( self.src_dir , self.usage_name)
    @property
    def consume_path(self):
        return os.path.join( self.src_dir , self.consume_name)
    @property
    def cut_ratio_path(self):
        return os.path.join( self.src_dir , self.cut_ratio_name)
    @property
    def discount_path(self):
        return os.path.join( self.src_dir , self.discount_name)
    
         
    @property
    def product_price_path(self):    
        return os.path.join(self.src_dir,self.sub_dir,f"{self.product_price_name}.xlsx")

    
if __name__=="__main__":
    config=TeaConfig()
    print(config.medical_price("荷叶"))

    

    
    
    
    