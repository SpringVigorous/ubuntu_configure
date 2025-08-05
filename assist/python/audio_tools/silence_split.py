import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
# 基于短时能量
def detect_silence_energy_zcr(audio_path, frame_length=2048, hop_length=512, energy_threshold=0.01, zcr_threshold=5):
    """
    基于短时能量和过零率检测停顿
    :param audio_path: 音频文件路径
    :param frame_length: 帧长（采样点）
    :param hop_length: 帧移（采样点）
    :param energy_threshold: 能量阈值（低于此值可能为停顿）
    :param zcr_threshold: 过零率阈值（高于此值可能为停顿）
    :return: 停顿区间列表（开始时间，结束时间，秒）
    """
    # 1. 加载音频
    y, sr = librosa.load(audio_path, sr=None)  # y: 音频信号，sr: 采样率
    duration = librosa.get_duration(y=y, sr=sr)  # 音频总时长（秒）
    
    # 2. 分帧计算特征
    # 短时能量（归一化）
    energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length).flatten()
    energy = energy / np.max(energy)  # 归一化到[0,1]
    
    # 过零率
    zcr = librosa.feature.zero_crossing_rate(y=y, frame_length=frame_length, hop_length=hop_length).flatten()
    zcr = zcr * sr  # 转换为每秒过零次数
    
    # 3. 计算每帧的时间戳（中心时间）
    frame_times = librosa.times_like(energy, sr=sr, hop_length=hop_length)
    frame_duration = frame_length / sr  # 每帧时长（秒）
    
    # 4. 判定停顿帧：能量低且过零率高
    is_silence = (energy < energy_threshold) & (zcr > zcr_threshold)
    
    # 5. 合并连续的停顿帧为区间
    silence_intervals = []
    in_silence = False
    start_time = 0
    
    for i, silence in enumerate(is_silence):
        if silence and not in_silence:
            # 停顿开始（取帧的起始时间）
            start_time = frame_times[i] - frame_duration / 2
            in_silence = True
        elif not silence and in_silence:
            # 停顿结束（取帧的结束时间）
            end_time = frame_times[i] + frame_duration / 2
            # 过滤过短的停顿（如小于0.1秒）
            if end_time - start_time > 0.1:
                silence_intervals.append((start_time, end_time))
            in_silence = False
    # 处理结尾的停顿
    if in_silence:
        silence_intervals.append((start_time, duration))
    if False:
        # 6. 可视化结果
        plt.figure(figsize=(12, 6))
        # 绘制波形
        plt.subplot(3, 1, 1)
        plt.plot(np.linspace(0, duration, len(y)), y)
        plt.title("音频波形")
        # 绘制能量
        plt.subplot(3, 1, 2)
        plt.plot(frame_times, energy, label="短时能量")
        plt.axhline(energy_threshold, color='r', linestyle='--', label="能量阈值")
        plt.title("短时能量")
        plt.legend()
        # 绘制过零率与停顿区间
        plt.subplot(3, 1, 3)
        plt.plot(frame_times, zcr, label="过零率")
        plt.axhline(zcr_threshold, color='g', linestyle='--', label="过零率阈值")
        for (s, e) in silence_intervals:
            plt.axvspan(s, e, color='gray', alpha=0.3, label="停顿区间" if s == silence_intervals[0][0] else "")
        plt.title("过零率与停顿检测结果")
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    return silence_intervals,duration

def srt_times(silence_times,duration):
    start=0
    results=[]
    for (s, e) in silence_times:
        results.append((start,s))
        start=e
    results.append((start,duration))
    return [{"start":s,"end":e} for (s, e) in results]


# 示例调用
if __name__ == "__main__":
    audio_path = r"F:\worm_practice\audio\8月5日.MP3"  # 替换为你的音频文件
    silences,duration = detect_silence_energy_zcr(
        audio_path,
        frame_length=2048,  # 约50ms（按44.1kHz采样率）
        hop_length=512,     # 约11ms，重叠率75%
        energy_threshold=0.02,  # 可根据实际音频调整
        zcr_threshold=1000     # 可根据噪声水平调整
    )
    print("检测到的停顿区间（秒）：")
    for i, (s, e) in enumerate(silences):
        print(f"停顿{i+1}: {s:.2f} - {e:.2f}，时长：{e-s:.2f}秒")
    import pandas as pd
    from pathlib import Path
    cur_path = Path(audio_path)  # 替换为你的音频文件
    pd.DataFrame(srt_times(silences,duration)).to_excel(cur_path.with_name(f"{cur_path.stem}_srt.xlsx"))
        
