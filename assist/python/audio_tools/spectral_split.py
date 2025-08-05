import librosa
import numpy as np
import matplotlib.pyplot as plt

def compute_spectral_entropy(y, frame_length=2048, hop_length=512):
    """计算每帧的谱熵"""
    # 1. 计算短时傅里叶变换（STFT）
    stft = librosa.stft(y, n_fft=frame_length, hop_length=hop_length)
    # 2. 取幅度谱并归一化
    magnitude = np.abs(stft)
    magnitude = magnitude / np.sum(magnitude, axis=0, keepdims=True)  # 按帧归一化
    # 3. 计算谱熵（避免log(0)）
    eps = 1e-10
    entropy = -np.sum(magnitude * np.log(magnitude + eps), axis=0)
    return entropy

def detect_silence_spectral_entropy(audio_path, frame_length=2048, hop_length=512, entropy_threshold=4.0):
    """基于谱熵检测停顿（谱熵越高，越可能是噪声/停顿）"""
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 计算谱熵
    entropy = compute_spectral_entropy(y, frame_length, hop_length)
    frame_times = librosa.times_like(entropy, sr=sr, hop_length=hop_length)
    frame_duration = frame_length / sr
    
    # 判定停顿帧（谱熵高于阈值）
    is_silence = entropy > entropy_threshold
    
    # 合并停顿区间（逻辑同前）
    silence_intervals = []
    in_silence = False
    start_time = 0
    for i, silence in enumerate(is_silence):
        if silence and not in_silence:
            start_time = frame_times[i] - frame_duration / 2
            in_silence = True
        elif not silence and in_silence:
            end_time = frame_times[i] + frame_duration / 2
            if end_time - start_time > 0.1:
                silence_intervals.append((start_time, end_time))
            in_silence = False
    if in_silence:
        silence_intervals.append((start_time, duration))
    
    # 可视化
    plt.figure(figsize=(12, 4))
    plt.subplot(2, 1, 1)
    plt.plot(np.linspace(0, duration, len(y)), y)
    plt.title("音频波形")
    plt.subplot(2, 1, 2)
    plt.plot(frame_times, entropy, label="谱熵")
    plt.axhline(entropy_threshold, color='r', linestyle='--', label="谱熵阈值")
    for (s, e) in silence_intervals:
        plt.axvspan(s, e, color='gray', alpha=0.3, label="停顿区间" if s == silence_intervals[0][0] else "")
    plt.title("谱熵与停顿检测结果")
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    return silence_intervals

# 示例调用
if __name__ == "__main__":
    audio_path = "test_audio.wav"
    silences = detect_silence_spectral_entropy(
        audio_path,
        frame_length=2048,
        hop_length=512,
        entropy_threshold=4.5  # 谱熵通常在2-6之间，噪声越高值越大
    )
    print("谱熵检测到的停顿区间：")
    for s, e in silences:
        print(f"{s:.2f} - {e:.2f}秒")