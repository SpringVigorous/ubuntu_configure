from dy_utility import dy_root,OrgInfo,DestInfo
import os



from pathlib import Path
import sys
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import remove_directories_and_files,logger_helper,UpdateTimeType,special_files,mp4_files,recycle_bin,move_file
from link_url import MessageManager
import pandas as pd
import re
class VideoManager:
    @staticmethod
    def real_name(del_name):
        name=OrgInfo(del_name).org_name
        return name
    
    @staticmethod
    def _del_video_impl(del_dir,file_name,exclude_strs:list=None):
        remove_directories_and_files(del_dir,posix_filter=[".mp4"],include_str=[file_name],exclude_strs=exclude_strs)
    
    @staticmethod
    def del_splited_movie(del_name,contain_nums:list=None):
        info=OrgInfo(del_name)
        series_name=info.series_name
        cur_dir=dy_root.dest_sub_dir(series_name)
        if not contain_nums:
            VideoManager._del_video_impl(cur_dir,del_name)
        else:
            for file in dy_root.dest_mp4_paths(info.org_name):
                if DestInfo(Path(file).name).scene_number not in contain_nums:
                    recycle_bin(file)

    @staticmethod
    def move_splited_movie(dest_dir,series_name,series_number,vidio_num):
        name=f"{series_name}_{series_number}"
        for file in dy_root.dest_mp4_paths(name):
            if int(DestInfo(file).scene_number)==int(vidio_num):
                move_file(file,dest_dir)
                break
                
    @staticmethod
    def del_org_movie(del_name):
        VideoManager._del_video_impl(dy_root.org_root,VideoManager.real_name(del_name))

    
    @staticmethod
    def def_movie_msg(del_name):
        del_name=VideoManager.real_name(del_name)
        #删除拆分后的文件
        df=MessageManager.load_json()
        df=df[df["name"]!=del_name]
        MessageManager.save_json(df)
        MessageManager.save_xlsx(df)
    
    
    @staticmethod
    def del_movie(del_name):
        VideoManager.del_org_movie(del_name)
        VideoManager.del_splited_movie(del_name)
        VideoManager.def_movie_msg(del_name)
    
    
    @staticmethod
    def rename_movie(old_name,new_name):
        
        from base import path_equal
        
        old_name=VideoManager.real_name(old_name)
        new_name=VideoManager.real_name(new_name)

        org_path=os.path.join(dy_root.org_root,dy_root.video_filename(old_name))
        #更改名
        if os.path.exists(org_path):
            new_path=os.path.join(dy_root.org_root,dy_root.video_filename(new_name))
            Path(org_path).rename(new_path)

        pattern = f"^{old_name}"+r"-(\d+)x(\d+)_(\d+)\.mp4$"
        def spc_fun(file_name:str):  # 定义一个函数spc_fun，接受一个字符串参数file_name
            return bool(re.match(pattern, file_name)) 
        
        src_split_dir=dy_root.dest_sub_dir(OrgInfo(old_name).series_name)
        files=special_files(src_split_dir,spc_fun)
        dest_split_dir=dy_root.dest_sub_dir(OrgInfo(new_name).series_name)
        
        for file in files:
            src_path=Path(file)
            dest_path=os.path.join(dest_split_dir, src_path.name.replace(old_name,new_name))
            src_path.rename(dest_path)
            
        
    @staticmethod
    def rename_tag(org_name,tag_name):
        
        logger=logger_helper("更改tag",f"{org_name}->{tag_name}")
        
        info= OrgInfo(org_name)
        series_name=info.series_name
        org_name=info.org_name
        if series_name==tag_name:
            logger.info("无需更改","tag相同")
            return
        
        
        df=MessageManager.load_json()
        mask = df["name"].isin([org_name])
        if mask.empty:
            return
        
        index_lst=[]
        sel_df=df[mask]
        count=sel_df.index.size
        if count>2:
            logger.warn(f"存在{count}个,只处理第一个",update_time_type=UpdateTimeType.STAGE)
        
        for index, row in sel_df.iterrows():
            org_tag,org_name,org_num=df.loc[index,["tag","name","video_num"]]
            if org_tag==tag_name:
                logger.info("无需更改","tag相同")
                continue
            
            
            df.loc[index,"tag"]=tag_name
            df.loc[index,"name"]=None
            df.loc[index,"video_num"]=None
            logger.info("修改df完毕",f"name:{org_name} tag:{org_tag} video_num:{org_num}")
            
            index_lst.append(index)
            break
            
        MessageManager.update_name(df,mask=mask)
        new_names=[df.loc[index,"name"] for index in index_lst ]
        
        for new_name in new_names:
            logger.update_target(detail=f"{org_name}->{new_name}")
            VideoManager.rename_movie(org_name,new_name)
            logger.info("修改mp4完毕",update_time_type=UpdateTimeType.STAGE)

        
        MessageManager.save_json(df)
        MessageManager.save_xlsx(df)


        

        


    
if __name__=="__main__":
    # VideoManager.del_movie("鼋头渚樱花_009")
    # VideoManager.rename_tag("鼋头渚夜樱_013","鼋头渚樱花")
    
    
    
    
    VideoManager.move_splited_movie()
    exit()
    
    contains="""鼋头渚樱花_004-1920x1080_001.mp4
            鼋头渚樱花_004-1920x1080_002.mp4
            鼋头渚樱花_004-1920x1080_003.mp4
            鼋头渚樱花_004-1920x1080_004.mp4
            鼋头渚樱花_004-1920x1080_007.mp4
            鼋头渚樱花_004-1920x1080_008.mp4
            鼋头渚樱花_004-1920x1080_009.mp4
            鼋头渚樱花_004-1920x1080_010.mp4
            鼋头渚樱花_004-1920x1080_011.mp4
            鼋头渚樱花_004-1920x1080_012.mp4
            鼋头渚樱花_004-1920x1080_013.mp4
            鼋头渚樱花_004-1920x1080_014.mp4
            鼋头渚樱花_004-1920x1080_015.mp4
            鼋头渚樱花_004-1920x1080_016.mp4
            鼋头渚樱花_004-1920x1080_017.mp4
            鼋头渚樱花_004-1920x1080_020.mp4
            鼋头渚樱花_004-1920x1080_023.mp4
            鼋头渚樱花_004-1920x1080_024.mp4
            鼋头渚樱花_004-1920x1080_025.mp4
            鼋头渚樱花_004-1920x1080_026.mp4
            鼋头渚樱花_004-1920x1080_027.mp4
            鼋头渚樱花_004-1920x1080_028.mp4
            鼋头渚樱花_004-1920x1080_029.mp4
            鼋头渚樱花_004-1920x1080_030.mp4
            鼋头渚樱花_004-1920x1080_031.mp4
            鼋头渚樱花_004-1920x1080_032.mp4
            鼋头渚樱花_004-1920x1080_033.mp4"""
    lst=[ DestInfo(file).scene_number for file in contains.split()]
    VideoManager.del_splited_movie("鼋头渚樱花_004",lst)