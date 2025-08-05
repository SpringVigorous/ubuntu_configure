from silence_split  import detect_silence_energy_zcr,srt_times
import pandas as pd
from pathlib import Path
import sys
import os
root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base  import generate_srt
def split_times(audio_path,xlsx_path):

    silences,duration = detect_silence_energy_zcr(
        audio_path,
        frame_length=2048,  # 约50ms（按44.1kHz采样率）
        hop_length=512,     # 约11ms，重叠率75%
        energy_threshold=0.02,  # 可根据实际音频调整
        zcr_threshold=1000     # 可根据噪声水平调整
    )
    # print("检测到的停顿区间（秒）：")
    # for i, (s, e) in enumerate(silences):
    #     print(f"停顿{i+1}: {s:.2f} - {e:.2f}，时长：{e-s:.2f}秒")

    pd.DataFrame(srt_times(silences,duration)).to_excel(xlsx_path,index=False)
        

        
        
def main():

    audio_path = r"E:\video\20250804\yinpin.mp3"  # 替换为你的音频文件
    xlsx_path=Path(audio_path).parent/"silence_srt.xlsx"
    #分割时间，输出 .xlsx
    # split_times(audio_path,xlsx_path)
    #修改.xlsx后，重新导入，生成srt文件
    
    df=pd.read_excel(xlsx_path)
    generate_srt(df.values.tolist(),xlsx_path.with_suffix(".srt"),"s")
    
if __name__ == "__main__":
    main()