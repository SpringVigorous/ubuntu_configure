import librosa
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

def extract_features(y, sr, frame_length=2048, hop_length=512):
    """提取用于GMM的特征：能量、过零率、谱熵"""
    energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length).flatten()
    zcr = librosa.feature.zero_crossing_rate(y=y, frame_length=frame_length, hop_length=hop_length).flatten()
    stft = librosa.stft(y, n_fft=frame_length, hop_length=hop_length)
    magnitude = np.abs(stft)
    magnitude = magnitude / np.sum(magnitude, axis=0, keepdims=True) + 1e-10
    entropy = -np.sum(magnitude * np.log(magnitude), axis=0)
    # 特征拼接（每行是一帧的特征）
    features = np.column_stack([energy, zcr, entropy])
    return features

def detect_silence_gmm(audio_path, frame_length=2048, hop_length=512):
    """用GMM检测停顿（需手动标注少量语音/停顿样本训练）"""
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    features = extract_features(y, sr, frame_length, hop_length)
    frame_times = librosa.times_like(features[:,0], sr=sr, hop_length=hop_length)
    frame_duration = frame_length / sr
    
    # ！！关键：手动标注训练样本（实际应用中需用标注工具）
    # 假设前100帧为语音，后100帧为停顿（需根据实际音频调整）
    # 生产环境中应使用标注好的数据集
    speech_features = features[:100]  # 语音样本
    silence_features = features[-100:]  # 停顿样本
    
    # 特征标准化
    scaler = StandardScaler()
    speech_scaled = scaler.fit_transform(speech_features)
    silence_scaled = scaler.transform(silence_features)
    all_scaled = scaler.transform(features)
    
    # 训练GMM模型
    gmm_speech = GaussianMixture(n_components=3, covariance_type='diag', random_state=42)
    gmm_silence = GaussianMixture(n_components=3, covariance_type='diag', random_state=42)
    gmm_speech.fit(speech_scaled)
    gmm_silence.fit(silence_scaled)
    
    # 预测：计算每帧属于语音/停顿的概率
    log_prob_speech = gmm_speech.score_samples(all_scaled)
    log_prob_silence = gmm_silence.score_samples(all_scaled)
    is_silence = log_prob_silence > log_prob_speech  # 停顿概率更高则判定为停顿
    
    # 合并停顿区间（同前）
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
    
    return silence_intervals

# 示例调用
if __name__ == "__main__":
    audio_path = "test_audio.wav"
    silences = detect_silence_gmm(audio_path)
    print("GMM检测到的停顿区间：")
    for s, e in silences:
        print(f"{s:.2f} - {e:.2f}秒")