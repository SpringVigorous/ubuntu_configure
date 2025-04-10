import os
import cv2
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from dy_unity  import dy_root ,DestInfo
import os
import subprocess
# LBP实现（需安装 scikit-image）
from skimage.feature import local_binary_pattern
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from pathlib import Path
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import hash_text,logger_helper,UpdateTimeType


def get_cover(video_path):
    """获取视频封面（优先查找独立文件，再尝试提取元数据）"""
    # 方式1：检查同目录下的封面文件
    temp_cover =os.path.join(dy_root.temp_dir, f"{hash_text(video_path)}.jpg")


    if os.path.exists(temp_cover):
        return cv2.imread(temp_cover)
    # 方式2：使用ffmpeg提取元数据中的封面
    try:
        # 生成临时封面文件

        cmd = f'ffmpeg -i "{video_path}" -an -vframes 1 -y "{temp_cover}"'
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        if os.path.exists(temp_cover):
            cover = cv2.imread(temp_cover)
            # os.remove(temp_cover)  # 清理临时文件
            return cover
    except Exception as e:
        print(f"无法提取 {video_path} 的封面: {str(e)}")
    
    return None
def extract_cover_features(cover_image):
    """提取封面特征"""
    if cover_image is None:
        return None
    
    # 颜色直方图 (HSV空间)
    hsv = cv2.cvtColor(cover_image, cv2.COLOR_BGR2HSV)
    hist_hsv = cv2.calcHist([hsv], [0,1,2], None, [8,8,8], [0,180,0,256,0,256])
    hist_hsv = cv2.normalize(hist_hsv, hist_hsv).flatten()
    
    # LBP纹理特征
    gray = cv2.cvtColor(cover_image, cv2.COLOR_BGR2GRAY)
    lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
    hist_lbp = np.histogram(lbp, bins=10, range=(0, 10))[0]
    hist_lbp = hist_lbp / hist_lbp.sum()
    
    # 合并特征
    return np.hstack([hist_hsv, hist_lbp])
def process_video_folder(folder):
    """处理整个视频文件夹"""
    video_files = [os.path.join(folder, f) for f in os.listdir(folder) 
                  if f.lower().endswith(('.mp4', '.avi', '.mov'))]
    
    return calculate_similarity(video_files)


def calculate_similarity(files):
    features = []
    valid_videos = []
    
    for video_path in tqdm(files, desc='处理封面'):
        cover = get_cover(video_path)
        if cover is not None:
            feature = extract_cover_features(cover)
            if feature is not None:
                features.append(feature)
                valid_videos.append(video_path)
    
    # 计算相似度矩阵
    sim_matrix = cosine_similarity(features)
    np.fill_diagonal(sim_matrix, 0)  # 排除自相似
    
    return valid_videos, sim_matrix



if __name__ == "__main__":
    # 1. 处理文件夹
    # folder_path =dy_root.org_root  # 替换为实际路径
    folder_path =dy_root.dest_sub_dir("鼋头渚夜樱")  # 替换为实际路径
    dir_name=Path(folder_path).name
    xls_path=os.path.join(dy_root.similarity_dir,f"{dir_name}-相似度.xlsx")
    
    logger=logger_helper(folder_path,xls_path)
    
    valid_videos, sim_matrix = process_video_folder(folder_path)
    logger.info("计算相似度",update_time_type=UpdateTimeType.STAGE)
    
    # 2. 生成报告
    df_report = pd.DataFrame({
        '视频文件': [os.path.basename(v) for v in valid_videos],
        '最相似封面': [os.path.basename(valid_videos[i]) for i in np.argmax(sim_matrix, axis=1)],
        '相似度': np.max(sim_matrix, axis=1)
    })
    

    df_report.sort_values('相似度', ascending=False,inplace=True)
    
    def check_name(row):
        org_name=DestInfo(row["视频文件"]).org_name
        same_org_name=DestInfo(row["最相似封面"]).org_name
        return 0 if org_name==same_org_name else 1
    
    df_report["flag"]=df_report.apply(lambda x: check_name(x),axis=1)
    
    # 创建一个临时列用于判断是否为重复对
    df_report['temp'] = df_report.apply(lambda row: tuple(sorted([row['视频文件'], row['最相似封面']])), axis=1)

    # 删除重复对
    df_report = df_report.drop_duplicates(subset='temp')

    # 删除临时列
    df_report = df_report.drop(columns='temp')
    
    logger.info("去重",update_time_type=UpdateTimeType.STAGE)
        # 可选：保存到Excel
    df_report.to_excel( xls_path, index=False)
    logger.info("输出成功",update_time_type=UpdateTimeType.ALL)
    
    # sim_matrix_df = pd.DataFrame(sim_matrix, index=df_report['视频文件'], columns=df_report['视频文件'])
    # # 可选：保存到Excel
    # sim_matrix_df.to_excel( os.path.join(dy_root.similarity_dir,f"{dir_name}-相似度矩阵.xlsx"), index=True)