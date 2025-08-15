from prohibited_detect import ProhibitedWordsDetector
import re
import pandas as pd
import sys
from collections.abc import Iterable
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import OCRProcessor,ImageHelper,unique,img_files,recycle_bin,logger_helper,UpdateTimeType,ZipUtility,write_to_txt_utf8_sig,is_empty_folder,clear_folder,cur_datetime_str,write_to_txt_utf8
from base import HtmlHelper,hash_text
from base.email import send_email ,ImageMode

import re

def split_by_pair_sig(s,left_sig='"',right_sig='"'):
    # 使用正则表达式提取所有双引号内的内容
            # 转义特殊字符，确保正则正确解析
    start_escaped = re.escape(left_sig)
    end_escaped = re.escape(right_sig)
    pattern=f'{start_escaped}(.*?){end_escaped}'
    match = re.findall(pattern, s, re.DOTALL)
    # 处理匹配结果，因为使用了多个分组，需要过滤空值
    results = []

        # 每个匹配是一个元组，取非空值
    for item in match:
        if not item:
            continue
        val=item.strip()
        if not val:
            continue
        results.append(item.strip())
    
    return results
    
def remove_whitespace(s):
    """使用正则表达式去除所有空白字符"""
    return re.sub(r'\s', '', s)

def split_by_multiple_delimiters(text, delimiters):
    """
    使用多个分隔符分割字符串
    
    参数:
        text: 需要分割的字符串
        delimiters: 分隔符列表，例如 [',', '/', ';', '；', '、', '|','：','=','・','\n','\u200b',"\\"]
    
    返回:
        分割后的字符串列表（过滤掉空字符串）
    """
    # 将分隔符转换为正则表达式模式
    pattern = '|'.join(re.escape(d) for d in delimiters)
    # 分割字符串
    parts = re.split(pattern, text)
    results=[]
    for part in parts:
        part=remove_whitespace(part)
        if not part:
            continue
        
        sigs=[('"','"'),
                ("'","'"),
                ("“","”"),
                ("《","》"),
                ("<",">"),
                ("【","】"),
                
                
                
                ('（','）'),
            ]
        has_sig=False
        for sig in sigs:
            left_sig,right_sig=sig
            sub_parts = split_by_pair_sig(part,left_sig,right_sig)
            if sub_parts:
                results.extend(sub_parts)
                has_sig=True
                break
        if not has_sig:
            results.append(part)
    
    # 过滤掉空字符串
    return list(filter(lambda x:x, results))

def combine_to_dict(data_list):
    """
    将列表项转换为字典，使用前两个值作为元组键，最后一个值作为目标值
    相同键的值会被收集到列表中
    
    参数:
        data_list: 包含三个元素的列表的列表，格式如 [(a1, b1, v1), (a2, b2, v2), ...]
        
    返回:
        以元组为键，值为列表的字典
    """
    result_dict = {}
    
    for item in data_list:
        # 确保每个项都有三个元素
        if len(item) != 3:
            raise ValueError("列表中的每个元素必须包含三个值")
        
        # 前两个值作为键（元组）
        key = (item[0], item[1]) if item[0]!=item[1] else (item[0],)
        # 第三个值作为目标值
        value = item[2]
        
        # 如果键已存在，添加到现有列表；否则创建新列表
        if key in result_dict:
            result_dict[key].append(value)
        else:
            result_dict[key] = [value]
    
    return result_dict


class prohibited_app:
    def __init__(self,xls_path:str,prohibited_words:list[str]=None):
        self._prohibited_words:list = []
        self._detector =None
        self._orc=None
        self.logger=logger_helper("图片敏感词检测")
        self._from_xlsx(xls_path)
    @property
    def  ocr(self):
        if self._orc is None:
            self._orc=OCRProcessor(lang='ch')
        return self._orc
        
    def _from_xlsx(self,xls_path:str):
        self.logger.stack_target(detail="加载违禁词")
        self.logger.reset_time()
        
        df = pd.read_excel(xls_path,"违禁词")
        self.add_prohibited_words(df["违禁词"].tolist())
        
        
        self.logger.info("完成",f"目录：{xls_path}",update_time_type=UpdateTimeType.STAGE)
        self.logger.pop_target()
        
        
        
    def save_prohibited_words(self,xls_path:str):
        self.logger.stack_target(detail="保存词库")
        try:
            df = pd.DataFrame(self.prohibited_words)
            df.to_excel(xls_path,sheet_name="违禁词")
        except Exception as e:
            self.logger.error("保存失败",e)

        self.logger.info("完成",f"目录：{xls_path}",update_time_type=UpdateTimeType.STAGE)
        self.logger.pop_target()
        
    @property
    def prohibited_words(self)->list:
        return unique(self._prohibited_words) if self._prohibited_words else []
        
    @property
    def detector(self):
        if not self._detector:
            self._detector = ProhibitedWordsDetector(self.prohibited_words)
        return self._detector
     
    def _add_prohibited_word(self,keyword:str):
        keyword=str(keyword)
        if keyword:
            keyword=keyword.strip()

        if not keyword:
            return
        
            # 定义要使用的分隔符
        delimiters = [',', '/', ';', '；', '、', '|','，','・','：','\u200b'," ",' ','。',"\n"]
        lst=split_by_multiple_delimiters(keyword, delimiters)
        self._prohibited_words.extend(filter(lambda x:x, lst))   
    def add_prohibited_words(self,words:list[str]):
        if not words: return
        
        if not isinstance(words,Iterable): 
            self._add_prohibited_word(str(words))
        else:
            for word in words: 
                self._add_prohibited_word(word)

    def detect(self,text):
        return self.detector.detect(text)



    def _detect_pics(self,img_paths:list|str,dest_paths:list|str=None,ocr_paths:list|str=None,auto_show=True)->list:
        if not img_paths: return
        
        if isinstance(img_paths,str) or isinstance(img_paths,Path): 
            img_paths=unique([img_paths])
        if not img_paths: return

        if not dest_paths:   
            dest_paths=[Path(img_path).with_stem(Path(img_path).stem+"_detect") for img_path in img_paths] 
        if not ocr_paths:   
            ocr_paths=[None]*len(img_paths) 
            
        results=[self._detect_pic(img_path,dest_path,ocr_path,auto_show) for img_path,dest_path,ocr_path in zip(img_paths,dest_paths,ocr_paths)]
        return results


    def _detect_folder_pics(self,img_dir,dest_dir,ocr_result_dir=None,auto_show=True)->list[tuple|list]:
        self.logger.stack_target(detail=f"当前文件夹{img_dir}")
        self.logger.update_time(UpdateTimeType.STAGE)
        
        img_paths=img_files(img_dir)
        dest_paths=[]
        ocr_paths=[]
        for img_path in img_paths:
            relative_path=Path(img_path).relative_to(img_dir)           
            dest_paths.append(os.path.join(dest_dir,relative_path))
            if ocr_result_dir:
                ocr_paths.append(os.path.join(ocr_result_dir,relative_path))
        infos=self._detect_pics(img_paths,dest_paths,ocr_paths,auto_show)
        
        self.logger.info("完成",update_time_type=UpdateTimeType.STAGE)
        self.logger.pop_target()
        return infos

    def _detect_pic(self,img_path,dest_img_path,ocr_path=None,auto_show=True)->tuple|list:
        self.logger.stack_target(detail=f"正在检测{img_path}")
        self.logger.update_time(UpdateTimeType.STEP)
        
        
        ocr_results = self.ocr.recognize_text(img_path)  
        #绘制文字识别结果
        if ocr_path:
            self.ocr.draw_results(img_path,ocr_results,ocr_path)




        boxes,texts,scores,subboxes = ocr_results
        org_text="".join(texts)
        def get_start_indices(str_list):
            """
            计算字符串列表中每个元素首字符的索引位置
            
            参数:
                str_list: 字符串列表
                
            返回:
                包含每个元素首字符索引的列表
            """
            indices = []
            current_position = 0  # 第一个字符串的起始索引为0
            
            for s in str_list:
                indices.append(current_position)
                # 累加当前字符串的长度，作为下一个字符串的起始索引
                current_position += len(s)
            
            return indices

        org_index=get_start_indices(texts)
        results=self.detector.detect(org_text)
        
        
        info:list=self.detector.detect_result(results)
        if not results:
            self.logger.info("成功","没有敏感词",update_time_type=UpdateTimeType.STEP)
            
            #若是没有敏感词，且不是强制显示，则直接返回
            dest_path=Path(dest_img_path)
            
            
            if auto_show:
                self.logger.pop_target()
                return str(dest_path),info
            else:
                dest_img_path=dest_path.with_stem(f"无敏感词_{dest_path.stem}")
        
        
        pos_index=self.detector.pos(results,org_index)

        #归类
        dest_index=combine_to_dict(pos_index)
        sorted_index=ImageHelper.sort_index(dest_index)
        sort_dict={}
        
        for index_key,detect_lst in sorted_index.items():
            cur_index=[]
            cur_detect=[]
            for item in detect_lst:
                cur_index.extend(item[0])
                cur_detect.extend(item[1])
                
            src_text="".join([texts[index] for index in unique(cur_index)])

            sort_dict[src_text]=cur_detect
        #绘制
        ImageHelper.draw(img_path,dest_img_path,boxes,sorted_index)
        
        
        
        #日志
        self.logger.trace("完成",f"比对结果输出到{dest_img_path}",update_time_type=UpdateTimeType.STEP)
        self.logger.pop_target()
        return str(dest_img_path),info,sort_dict

        
    def detect_fold(self,img_dir,detect_result_dir,ocr_result_dir=None,auto_show=True):
        self.logger.stack_target(detail=f"{img_dir}->{detect_result_dir}")
        self.logger.update_time(UpdateTimeType.ALL)
        self.logger.info("开始")
        
        if is_empty_folder(img_dir):
            self.logger.error("文件夹为空",f"{img_dir}",update_time_type=UpdateTimeType.STAGE)
            return
        
        timestamp = cur_datetime_str()
        out_name=f"违禁词检测结果_{timestamp}"
        #输出检测结果
        results=self._detect_folder_pics(img_dir,detect_result_dir,ocr_result_dir,auto_show=auto_show)
        
        if not results:
            self.logger.error("检测结果为空",update_time_type=UpdateTimeType.STAGE)
            return
        
        def _arrage_result(info):
            _info="\n".join([f"'{key}'->【{'】;【'.join(val)}】"for key,val in info.items()])
            return f"详细信息如下：\n{_info}"
        
        text_contents=[]
        for result in results:
            file_path,info,sorted_dict=result
            text_info=ProhibitedWordsDetector.results_txt(info)

            text_contents.append(f"{Path(file_path).relative_to(detect_result_dir)}:\n{text_info}\n\n{_arrage_result(sorted_dict)}\n\n")
        if text_contents:
            txt_path=os.path.join(detect_result_dir,f"{out_name}.txt")
            self.logger.stack_target(detail=f"保存结果->{txt_path}")
            write_to_txt_utf8_sig(txt_path,"\n".join(text_contents))
            self.logger.info("记录结果:完成",update_time_type=UpdateTimeType.STAGE)
            self.logger.pop_target()



        #邮件头
        
        heads=["编号","结果","图片"]
        bodys=[
            [(index+1,0,"top"),(f"{ProhibitedWordsDetector.results_txt_short(row[1])}\n\n{_arrage_result(row[2])}",0,"top","red"),((hash_text(row[0]),Path(row[0]).relative_to(detect_result_dir)),1,"center")]
            for index,row in enumerate(results)
        ]
        html_body=HtmlHelper.html_tab(heads,bodys)
        #把结果保存为网页
        write_to_txt_utf8(os.path.join(detect_result_dir,f"{out_name}.html"),html_body)
        
        
        #压缩包
        zipper=ZipUtility()
        source=Path(detect_result_dir)
        zip_path=os.path.join(source.parent,"zip",f"{source.name}_{timestamp}.zip")
        zipper.compress(detect_result_dir,zip_path)
        self.logger.stack_target(detail=f"打包结果->{zip_path}")
        self.logger.info("打包:完成",update_time_type=UpdateTimeType.STAGE)
        self.logger.pop_target()
        
        
        #发送邮件
        email_reciever="350868206@qq.com"
        self.logger.stack_target(detail=f"发送邮件->{email_reciever}")
        attachment_path=[item[0] for item in results]
        attachment_path.append(zip_path)
        send_email(email_reciever,out_name,html_body,body_type="html",attachment_path=attachment_path,image_mode=ImageMode.INSERT)
        self.logger.info("邮件：完成","检测结果",update_time_type=UpdateTimeType.STAGE)
        self.logger.pop_target()

        

        
        if is_empty_folder(detect_result_dir):
            return
        #清空
        clear_folder(img_dir)
        self.logger.info("成功",f"共{len(results)}个文件",update_time_type=UpdateTimeType.ALL)

    
        
        pass
def main(img_dir,output_dir,ocr_dir):
    
        #清空
    # clear_folds(img_dir)
    clear_folder(output_dir)
    
    xlsx_path=r"F:\worm_practice\taobao\违禁词\违禁词.xlsx"
   
    app=prohibited_app(xlsx_path)
    org_xlsx_path=Path(xlsx_path)
    #输出违禁词库
    app.save_prohibited_words(org_xlsx_path.with_stem(org_xlsx_path.stem+"_prohibited_words"))
    #输出检测结果
    app.detect_fold(img_dir,output_dir,ocr_dir,auto_show=False)


if __name__ == '__main__':
    img_dir=Path(r"F:\worm_practice\taobao\五味食养\images")
    name=img_dir.name
    
    output_dir= str(img_dir.with_name(f"{name}_prohibite"))
    ocr_dir=str(img_dir.with_name(f"{name}_ocr"))


    

    
    main(img_dir,output_dir,ocr_dir)
