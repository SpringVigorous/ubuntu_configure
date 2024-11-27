import os
import pandas as pd 
import numpy as np 
class TeaConfig:
    def __init__(self,org_dir=r"E:\花茶\价格") -> None:
        self.src_dir=org_dir
        self.purchase_name="采购价格"
        self.usage_name="产品用量.xlsx"
        self.consume_name="额外费用.xlsx"
        self.cut_ratio_name="扣费比率.xlsx"
        self.discount_name="优惠活动.xlsx"
        self.sub_dir="详情"
        self.product_medical_name="产品药材价格"
        self.product_price_name="产品价格"
        self.init_data()
        pass
    
    @staticmethod
    def search_mathes_by_name(df,col_name,val):
        return df[col_name].str.contains(val, case=False, na=False)
    
    @staticmethod
    def search_rows_by_name(df,col_name,val,target_name):
        rows= df.loc[TeaConfig.search_mathes_by_name(df,col_name,val),target_name]
        if not rows.empty:
            return rows.values
        print(f"查找{target_name}失败，未找到{col_name}:{val}")
        return []
    
    def medical_price(self,name):
        rows=TeaConfig.search_rows_by_name(self.purchase_price_df,'产品',name,'单价')
        return rows[0] if len(rows)>0 else 0.0

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

        product_df= pd.DataFrame({"产品":self.product_medical_prices_df["产品"]})
        print(type(product_df))
        
        
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
        
        
        # 读取 "单包" 表
        df = pd.read_excel(self.consume_path, sheet_name='单包')
        self.fix_pack_info = (df['单价'].sum(),df['质量'].sum())
        
        # 读取 "单盒" 表
        df = pd.read_excel(self.consume_path, sheet_name='单盒')
        self.fix_box_info = (df['单价'].sum(),df['质量'].sum())
        
        # 读取 "单次" 表
        df = pd.read_excel(self.consume_path, sheet_name='单次')
        self.fix_bill_info = (df['单价'].sum(),df['质量'].sum())
        
        

        df = pd.read_excel(self.cut_ratio_path, sheet_name='扣费比率')
        self.fix_cut_ratio = df['比率'].sum()
        
        
        self.each_discount_df = pd.read_excel(self.discount_path, sheet_name='跨店满减')
        self.normal_discount_df = pd.read_excel(self.discount_path, sheet_name='满减')
        
        normal_rebate_df= pd.read_excel(self.discount_path, sheet_name='一口价折扣')
        self.normal_cut_radio=1-normal_rebate_df.loc[0]["折扣"]
        org_rebate_df= pd.read_excel(self.discount_path, sheet_name='定价折扣')
        self.org_rebate=org_rebate_df.iloc[0]["折扣"]
        unit_path=os.path.join(self.src_dir, "产品规格.xlsx")
        
        self.box_unit_df=pd.read_excel(unit_path,sheet_name="盒规格")
        self.deliver_unit_df=pd.read_excel(unit_path,sheet_name="快递规格")
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

    

    
    
    
    