import sys

from pathlib import Path
import os
from typing import Callable
import numpy as np  # 用于条件判断
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import (
    logger_helper,
    UpdateTimeType,
    arabic_numbers,
    priority_read_json,
    xml_tools,
    concat_dfs,
    unique_df,
    download_sync,
    ThreadPool,
    merge_df,
    update_col_nums,
    assign_col_numbers,
    OCRProcessor,
    fix_url,
    concat_unique,
    content_same,
    sub_df,
    set_attr,
    get_attr,
    except_stack,
    exception_decorator,
    jpg_files,
    unique,
    path_equal,
    json_files,
    read_from_json_utf8_sig,
    df_empty,
    find_rows_by_col_val,
    sequence_num_file_path
)
import pandas as pd
from taobao_config import *
from taobao_tools  import *
import threading

pic_type_map={0:"主图",1:"详图",3:"Sku"}

class tb_manager():
    _instance = None
    _lock = threading.Lock()    
    _initialized = False  # 初始化标志位

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    # 创建实例但不调用 __init__
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        # 确保初始化仅执行一次
        if  self.__class__._initialized:
            return
        
        with self.__class__._lock:
            if  self.__class__._initialized:
                return
            # 实际初始化逻辑

            self.logger=logger_helper("taobao_manager")
            
            self._lock = threading.Lock()
            
            self._read_xlsx_df()
        
            # 初始化标志位
            self.__class__._initialized = True
            
    @property
    def shop_df(self)->pd.DataFrame:

        return set_attr(self._shop_df,"name",shop_name)
    
    
    @property
    def product_df(self)->pd.DataFrame:
        return set_attr(self._product_df,"name",product_name)
    
    @property
    def pic_df(self)->pd.DataFrame:
        return set_attr(self._pic_df,"name",pic_name)
    @property
    def ocr_df(self)->pd.DataFrame:
        return set_attr(self._ocr_df,"name",ocr_name)
    
    def __del__(self):
        logger=self.logger
        logger.update_target("保存数据",xlsx_file)
        logger.update_time(UpdateTimeType.STAGE)
        # 清理资源（如关闭文件、释放网络连接等）
        self._save_xlsx_df()
        logger.info("完成",update_time_type=UpdateTimeType.STAGE)
        
        
        
    @classmethod
    def destroy_instance(cls):
        with cls._lock:
            if cls._instance:
                # 手动触发析构函数
                cls._instance = None
                cls._initialized = False
 


    def has_id_val(self,df:pd.DataFrame,id_name:str,id_val):
        with self._lock:

            if df.empty:
                return False
            
            mask=df[id_name]==id_val
            return mask.any()
                    
            
            

    def has_shop_id(self,shopId:str)->bool:
        return self.has_id_val(self.shop_df,shop_id,shopId)
    
    def has_item_id(self,itemId:str)->bool:
        return self.has_id_val(self.product_df,item_id,itemId)
    
    def has_pic_url(self,pic_url:str)->bool:
        return self.has_id_val(self.pic_df,pic_url_id,pic_url)
    
    def has_ocr_id(self,pic_url:str)->bool:
        return self.has_id_val(self.ocr_df,pic_url_id,pic_url)

                    
    def _read_xlsx_df(self):
        
        logger=self.logger
        logger.update_target("读取数据",xlsx_file)
        logger.update_time(UpdateTimeType.STAGE)
        def init_fetch_id(df:pd.DataFrame):
            if df_empty(df):
                return df
            if not_fetch_id in df.columns.tolist():
                df[not_fetch_id].fillna(0, inplace=True)
            else:
                df[not_fetch_id]=0
            df[not_fetch_id]=df[not_fetch_id].astype(int)
            return df
        
        if os.path.exists(xlsx_file):
            with pd.ExcelFile(xlsx_file) as reader:
                sheetnames=reader.sheet_names
                def get_df(name:str,str_col_names:list|str=None)->pd.DataFrame:
                    if name not in sheetnames:
                        return pd.DataFrame()
                    df=reader.parse(name)
                    
                    if str_col_names:
                        if isinstance(str_col_names,str):
                            str_col_names=[str_col_names]
                        for col_id in str_col_names:
                            if col_id in df.columns:
                                df[col_id]=df[col_id].astype(str)
                    return df
                with self._lock:
                    self._shop_df = init_fetch_id(get_df(shop_name,[shop_id,user_id,seller_id]))
                    self._product_df = init_fetch_id(get_df(product_name,[shop_id,item_id]))
                    self._pic_df =  get_df(pic_name,[item_id])
                    self._ocr_df=get_df(ocr_name,[item_id])
        else:
            logger.trace("文件不存在",update_time_type=UpdateTimeType.STAGE)
            with self._lock:
                self._shop_df=pd.DataFrame()
                self._product_df=pd.DataFrame()
                self._pic_df=pd.DataFrame()
                self._ocr_df=pd.DataFrame()
        

        
        logger.info("完成",update_time_type=UpdateTimeType.STAGE)
            
            
    @exception_decorator(error_state=False)
    def _save_xlsx_df(self):
        logger=self.logger
        logger.update_time(UpdateTimeType.STAGE)
        logger.trace("开始")
        pic_summary_df=self.summary_pic_df()
        ocr_summary_df=self.summary_ocr_df()
        
        def _save_imp(xlsx_path:str):
            logger.update_target("保存数据",xlsx_path)
            with self._lock:
                with pd.ExcelWriter(xlsx_path,mode="w") as w:
                    self._shop_df.to_excel(w, sheet_name=shop_name, index=False)
                    self._product_df.to_excel(w, sheet_name=product_name, index=False)
                    self._pic_df.to_excel(w, sheet_name=pic_name, index=False)
                    self._ocr_df.to_excel(w, sheet_name=ocr_name, index=False)
                    if not pic_summary_df.empty:
                        pic_summary_df.to_excel(w, sheet_name=f"{pic_name}_汇总", index=False)
                    if not ocr_summary_df.empty:
                        ocr_summary_df.to_excel(w, sheet_name=f"{ocr_name}_汇总", index=False)
        
        try:
            _save_imp(xlsx_file)
        except:
            xlsx_path=sequence_num_file_path(xlsx_file)
            logger.error("失败",f"备份到{xlsx_path},具体错误信息入下：\n{except_stack()}\n", update_time_type=UpdateTimeType.STAGE)
            logger.update_time(UpdateTimeType.STAGE)
            _save_imp(xlsx_path)

        logger.trace("完成",update_time_type=UpdateTimeType.STAGE)

    #更新：返回 更新后的数据，和新增的数据
    def update_shop_df(self,shop_df:pd.DataFrame)->pd.DataFrame:
        with self._lock:
            self._shop_df,shop_df=self._update_df(self.shop_df,shop_df,keys=[shop_name_id])      
            return shop_df
        
    #更新：返回 更新后的数据，和新增的数据
    def update_product_df(self,product_df:pd.DataFrame):
        with self._lock:
        
            self._product_df,new_df=self._update_df(self.product_df,product_df,keys=[item_id],
                                                arrage_fun=arrage_product_df,
                                                new_data_func=None)
            return new_df
            
            
    #更新：返回 更新后的数据，和新增的数据
    def update_pic_df(self,pic_df:pd.DataFrame):
        logger=self.logger
        with self._lock:
            def _arrage_pic(df:pd.DataFrame)->pd.DataFrame:
                result=self.product_df.set_index(item_id)[num_id].to_dict()
                logger.trace("显示字典对:",f"{result}")
                return arrange_pic(df,result)
            # print(pic_df)
            
            # print(self._pic_df)
                
            result=self._update_df(self.pic_df,pic_df,keys=[pic_url_id],arrage_fun=_arrage_pic,
                                                new_data_func=None)
            if not result:
                return pd.DataFrame()
            
            self._pic_df,pic_df=result
            return pic_df
    #返回  【更新后数据，新增的数据】：pd.DataFrame
    def update_ocr_df(self,ocr_df:pd.DataFrame):
        with self._lock:
            
            # print(self.ocr_df)
            # print(ocr_df)
            def sort_ocr_df(df:pd.DataFrame)->pd.DataFrame:
                return df.sort_values(by=[name_id],ascending=True)
            
            
            self._ocr_df,ocr_df=self._update_df(self.ocr_df,ocr_df,keys=[name_id],
                                                arrage_fun=sort_ocr_df,
                                                new_data_func=None)
            return ocr_df
    
    @exception_decorator(error_state=False)
    def _update_df(self,
                  org_df:pd.DataFrame,
                  new_df:pd.DataFrame,keys:list|tuple,
                  arrage_fun:Callable[[pd.DataFrame],pd.DataFrame]=None,
                  new_data_func:Callable[[pd.Series],None]=None,
                  )->tuple[pd.DataFrame,pd.DataFrame]:
        df_name=get_attr(org_df,"name")
        org_df=org_df.copy()
        
        logger=self.logger
        logger.update_target("更新数据",df_name)
        logger.update_time(UpdateTimeType.STAGE)
        
        result_df=concat_unique([org_df,new_df],keys=keys)
        if arrage_fun:
            result_df=arrage_fun(result_df)
        
        cut_df=pd.DataFrame()
        
        if not content_same(org_df,result_df):
            cut_df=sub_df(result_df,org_df,keys)

        logger.info("完成",f"新增{len(cut_df)}条记录",update_time_type=UpdateTimeType.STAGE)
        
        
        if new_data_func and not cut_df.empty:
            logger.update_target("处理新增数据",f"共{len(cut_df)}行")
            logger.trace("开始",update_time_type=UpdateTimeType.STAGE)
            
            for index,row in cut_df.iterrows():
                    logger.stack_target(f"处理新增数据:{index}",str(row))
                    logger.update_time(UpdateTimeType.STEP)
                    try:
                        new_data_func(row)
                        logger.info("完成",update_time_type=UpdateTimeType.STEP)
                    except :
                        logger.error("处理异常",except_stack(),update_time_type=UpdateTimeType.STEP)
                    finally:
                        logger.pop_target()
            logger.info("完成",update_time_type=UpdateTimeType.STAGE)
            
        return [result_df,cut_df]

    def summary_pic_df(self)->pd.DataFrame:
        with self._lock:
            pic_df=self.pic_df.groupby([item_id, type_id]).size()
            summary_df = pic_df.reset_index(name='counts')
            # 将 type 的 0 和 1 转换为两列
            pic_summary_df = (summary_df.pivot(index="itemId", columns="type", values="counts")
                        .fillna(0)  # 填充缺失值为0（处理没有对应type的情况）
                        .rename(columns=lambda x: f"{x}-count")  # 动态生成列名（例如 0-count, 1-count, 2-count）
                        .reset_index()  # 将 itemId 从索引恢复为普通列
                        )

            # 添加 lost 列
            pic_summary_df["lost"] = np.where(
                (pic_summary_df["0-count"] > 2) & (pic_summary_df["1-count"] > 3),  # 同时满足两个条件
                0,  # 条件为真时返回 0
                1   # 条件为假时返回 1
            )
            pic_summary_df=pd.merge(self.product_df,pic_summary_df,on=item_id,how="outer")
            
            
            if title_except_flags:
                # 使用正则表达式过滤不包含指定关键词的行
                mask=pic_summary_df['title'].str.contains('|'.join(title_except_flags), regex=True, case=False, na=False)
                pic_summary_df = pic_summary_df[~mask]
            
            return pic_summary_df.sort_values(by=[num_id],ascending=True)

    def summary_ocr_df(self)->pd.DataFrame:
        
        ocr_df=None
        with self._lock:
            if not self.ocr_df.empty:
                ocr_df=self.ocr_df.copy()
        if df_empty(ocr_df):
            return pd.DataFrame()
        

        
        # ocr_df["col_num"]=ocr_df.groupby(ocr_text_id).cumcount()

        # # 使用 pivot 将 name 平铺到多列
        # result = ocr_df.pivot_table(
        #     index=ocr_text_id, 
        #     columns="col_num", 
        #     values=name_id, 
        #     aggfunc="first"  # 保留第一个值，忽略重复
        #     ).reset_index()

        # # 重命名列（例如 name_0, name_1）
        # result.columns = [ocr_text_id] + [f"{name_id}_{i}" for i in range(len(result.columns)-1)]
        
        # 生成唯一索引（text + 动态列号）
        
        mask=ocr_df[ocr_text_id].isna()
        none_df=ocr_df[mask]
        ocr_df=ocr_df[~mask]
        ocr_df["col_num"] = ocr_df.groupby(ocr_text_id).cumcount()

        # 设置多级索引并转换
        result = (
            ocr_df.set_index([ocr_text_id, "col_num"])[name_id]
            .unstack()
            .reset_index()
            .rename_axis(columns=None)
        )

        # 重命名列
        result.columns = [ocr_text_id] + [f"{name_id}_{i}" for i in range(result.shape[1]-1)]
        return result.sort_values(by=f"{name_id}_0",ascending=True)
    
    def update_sku_pic_from_cache_json(self)->pd.DataFrame:
        
        result_df=pd.DataFrame()
        
        sku_lst=[]
        for file in json_files(main_dir):
            data=read_from_json_utf8_sig(file)
            if not data:
                continue
            lst=sku_infos_from_main(data)
            if lst:
                sku_lst.extend(lst)
        if not sku_lst:
            return result_df
        
        product_df=pd.DataFrame(sku_lst)
        product_df[item_id]=product_df[item_id].astype(str)
        result_df=self.update_pic_df(product_df)
        return result_df

    @exception_decorator(error_state=False)
    def clear_cache(self):
        from base import txt_files,xlsx_files,remove_directories_and_files,recycle_bin
        
        remove_directories_and_files(org_pic_dir,posix_filter=[".txt",".xlsx"])

        @exception_decorator(error_state=False)
        def _clear_dir(root_dir):
            results=[{"path":file }for file in json_files(root_dir)]
            if not results:
                results
            df=pd.DataFrame(results)
            # 定义分割函数，直接返回 name 和 num
            def split_path(path_str):
                parts = Path(path_str).stem.split("_")
                name = parts[1] if len(parts) > 1 else "unknown"  # 默认值
                num = parts[2] if len(parts) > 2 else "0"         # 默认值
                return pd.Series({"name": name, "num": int(num),"size":os.path.getsize(path_str)})
            
            df[["name", "num","size"]]=df["path"].apply(split_path)
            for key,group_df in df.groupby("name"):
                if group_df.shape[0]==1:
                    continue
                sort_df=group_df.sort_values("size",ascending=False)
                for file in sort_df["path"].values[1:]:
                    recycle_bin(file)

        _clear_dir(main_dir)
        _clear_dir(desc_dir)

    @exception_decorator(error_state=False)
    def get_undone_df(self)->list[pd.DataFrame] :
        
        """获取所有产品列表"""
        download_pic_nums=[Path(file_path).stem for file_path in jpg_files(org_pic_dir)]
        #爬取不完全的，即图片信息仅有个别几张的
        summary_df=self.summary_pic_df()
        #skuinfo
        sku_df=self.update_sku_pic_from_cache_json() if fetch_sku_from_cache else pd.DataFrame()
        
        
        with self._lock:
            #未下载的
            pic_df=self.pic_df
            mask=pic_df[name_id].isin(filter(lambda x:x,download_pic_nums))
            undownload_df=pic_df[~mask].copy()
            downloaded_df=pic_df[mask]
            
            if not sku_df.empty:
                if not undownload_df.empty:
                    undownload_df=pd.concat([undownload_df,sku_df])
                else:
                    undownload_df=sku_df
            
            #未识别的
            unocr_df=sub_df(downloaded_df,self.ocr_df,keys=name_id)
            
            #没有爬取详情的
            hasDetail_df=pic_df.drop_duplicates(subset=[item_id],ignore_index=True)
            

            
            # product_df=self.product_df.dropna(subset=[not_fetch_id]).query(f"{not_fetch_id} > 0")
            # product_df=self.product_df.query(f"{not_fetch_id}.notna() | {not_fetch_id} < 1")
            product_df=self.product_df.query(f"{not_fetch_id} < 1")
            nodetail_df=sub_df(product_df,hasDetail_df,keys=item_id)
            

            if not summary_df.empty and force_update:
                summary_df=summary_df[summary_df['lost']>0]
                if nodetail_df.empty:
                    nodetail_df=summary_df
                else:
                    summary_df=summary_df[nodetail_df.columns.to_list()] 
                    nodetail_df=concat_dfs(nodetail_df,summary_df)
            
            return [nodetail_df,undownload_df,unocr_df]
        

    @exception_decorator(error_state=False)
    def rename_pic_name(self,fix_count:int=3)->bool:
        
        logger=self.logger
        logger.update_target("重命名图片",f"产品编号固定位:{fix_count}个字符")
        
        logger.trace("开始")
        def get_new_name(name:str):
            if not name:return name
            cur_path=Path(name)
            nums=[int(num) for num in cur_path.stem.split("_")]
            new_name=get_pic_name(*nums[:3],fix_count)
            return str(cur_path.with_stem(new_name))
        
        def rename_df(df:pd.DataFrame):
            if df.empty:return True
           
            logger.trace(f"正在处理:{get_attr(df,"name")}",update_time_type=UpdateTimeType.STAGE)
            dest_df=df[name_id].apply(lambda x:get_new_name(x))
            if dest_df.empty:return 
            df[name_id]=dest_df
            
            return True

        
        with self._lock:
            if (rename_df(self.pic_df) and rename_df(self.ocr_df)):
                #重新排序
                self.ocr_df.sort_values(by=[name_id],ascending=True,inplace=True)
            else:
                return False

        pic_files= jpg_files(org_pic_dir)
        pic_files.extend(jpg_files(ocr_pic_dir))
        for file_path in pic_files:
            new_path=get_new_name(file_path)
            if path_equal(new_path,file_path):
                continue
            
            logger.trace(f"{file_path}->{new_path}")
            os.rename(file_path,new_path)
    
        return True
    
    def classify_pics(self)->None:
        logger=self.logger
        logger.update_target("图片归类",f"以商品num进行分类")
        logger.trace("开始")
        def move_imp(pic_path:str,sub_dir_name:str):
            cur_path=Path(pic_path)
            if cur_path.parent.stem!=sub_dir_name:
                return
            new_path=dest_file_path(cur_path.parent,cur_path.name)
            os.rename(pic_path,new_path)
        def classify_pic_imp(pic_dir:str):
            logger.update_target(detail=f"处理:{pic_dir}")
            logger.update_time(UpdateTimeType.STAGE)
            logger.trace("开始")
            for pic_path in jpg_files(pic_dir):
                move_imp(pic_path,Path(pic_dir).stem)
            logger.trace("完成",update_time_type=UpdateTimeType.STAGE)
            
        #移动图片
        classify_pic_imp(org_pic_dir)
        classify_pic_imp(ocr_pic_dir)

    @exception_decorator(error_state=False)
    def separate_ocr_results(self):
        logger=self.logger
        with self._lock:
            if self.ocr_df.empty or self.pic_df.empty:
                
                return
            ocr_df=pd.merge(self.ocr_df,self.pic_df,on=[name_id],how="inner")
            shop_good_df=pd.merge(self.product_df,self.shop_df,on=[shop_id],how="outer")
            groups=ocr_df.groupby(item_id)
            for name,df in groups:
                if df.empty:
                    continue
                name=df[name_id].iloc[0].split("_")[0]
                # group_df.to_excel(f"{group[0]}.xlsx",index=False)
                

                logger.update_target("拆分识别信息",os.path.join(org_pic_dir,name))

                txt_path=os.path.join(result_dir,f"{name}-识别结果.txt")

                last_type=None
                with open(txt_path,"w",encoding="utf-8-sig") as f:
                    
                    def format_len(str_val:str,len:int=50,set_newline=False):
                        return f"{str_val.center(len, '-')}" + ("\n" if set_newline else "")
                        
                    
                    for _,row in df.iterrows():
                        val=row[ocr_text_id]
                        if not val or not isinstance(val,str):
                            continue
                        pic_type=int(row[name_id].split("_")[1])
                        if last_type != pic_type:
                            type_str=pic_type_map.get(pic_type,None)
                            if not type_str:
                                continue
                            if last_type==None:
                                #查找店铺信息
                                rows:pd.DataFrame=find_rows_by_col_val(shop_good_df,item_id,row[item_id])
                                if not df_empty(rows):
                                    vals:pd.Series=rows.loc[0:]
                                    
        
                                    
                                    f.write(format_len("店铺信息",set_newline=True))
                                                    
                                    @exception_decorator(error_state=False)
                                    def write_good_info(title_str:str, val_id:str):
                                        val=vals.get(val_id,None)
                                        if df_empty(val):
                                            return
                                        f.write(f"{format_len(title_str,len=5)}{val.values[0]}\n")
                                        
                                    write_good_info("店铺名:",shop_name_id)
                                    write_good_info("店铺链接:",home_url_id)
                                    write_good_info("产品标题:",title_id)
                                    write_good_info("产品链接:",item_url_id)
                                    write_good_info("产品销量:",sales_vol_id)

                                                   
                                                   

                            f.write(format_len(type_str,set_newline=True))
                            last_type=pic_type
                        
                        f.write(f"{val.replace(";","\n")}\n\n\n")
                logger.trace("成功",txt_path,update_time_type=UpdateTimeType.STEP)
                
                # df.to_excel(dest_file_path(org_pic_dir,f"{name}-识别结果.xlsx"),index=False)

                
    def init_product_df_product_name(self)->pd.DataFrame:   
        with self._lock:
            product_df=self.product_df
            mask=product_df[goods_name_id].isna() 
            dest_df=product_df[mask]
            
            product_df.loc[mask,goods_name_id]=dest_df[title_id].apply(lambda x:get_product_name_from_title(x))

            return product_df
                
if __name__=="__main__":
    manager=tb_manager()
    
    manager.clear_cache()
    exit()
    
    from base import read_from_json_utf8_sig
    

    dir_temp=r"C:\Users\Administrator\Desktop\备份"
    
    pic_df=pd.read_excel(f"{dir_temp}/pic_df.xlsx")
    pic_df1=pd.read_excel(f"{dir_temp}/pic_df1.xlsx") 
    pic_df[item_id]=pic_df[item_id].astype(str)
    pic_df1[item_id]=pic_df1[item_id].astype(str)
    
    shop_json_path=r"F:\worm_practice\taobao\店铺\shop_293825603_1.json"

    shop_dict=org_shop_dict_from_product(read_from_json_utf8_sig(shop_json_path))
    if shop_dict:
        shop_df=pd.DataFrame([shop_dict])
    
    ocr_df=manager.update_shop_df(shop_df)
    print(ocr_df)
    print(pic_df)
    print(pic_df1)
    
    
    ocr_df=manager.update_pic_df(pic_df)
    print(ocr_df)
    ocr_df=manager.update_pic_df(pic_df1)
    print(ocr_df)
    