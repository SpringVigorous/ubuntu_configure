import os
import json
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydub import AudioSegment
from pydub.silence import split_on_silence
from vosk import Model, KaldiRecognizer
import threading
from pathlib import Path
from base import logger_helper,UpdateTimeType
class VoskBatchTranscriber:
    """
    使用Vosk和多线程处理长音频文件的转录器。
    """
    def __init__(self, model_path, max_workers=None):
        """
        初始化转录器。
        
        Args:
            model_path (str): Vosk模型目录的路径。
            max_workers (int, optional): 线程池最大线程数。默认为CPU核心数。
        """
        self.model_path = model_path
        self.max_workers = max_workers if max_workers else os.cpu_count()
        self.logger=logger_helper(self.__class__.__name__,f"模型{model_path},workers_count:{max_workers}")
        
        with self.logger.raii_target("加载模型"):
            # 加载Vosk模型（全局共享，线程安全）
            self.logger.trace(f"正在加载")
            if not os.path.exists(model_path):
                raise ValueError(f"模型路径不存在: {model_path}")
            self.model = Model(model_path)
            self.logger.trace("加载成功",update_time_type=UpdateTimeType.STAGE)
        
        # 用于保护结果列表的锁
        self._results_lock = threading.Lock()
        self.all_segments = []

    def check_and_preprocess_audio(self, audio_path, target_sample_rate=16000, target_channels=1):
        """
        检查并预处理音频文件，确保其为Vosk要求的格式（16kHz，单声道）。
        
        Args:
            audio_path (str): 输入音频文件路径。
            target_sample_rate (int): 目标采样率。
            target_channels (int): 目标声道数。
            
        Returns:
            str: 预处理后的标准WAV文件路径。
        """
        with self.logger.raii_target(f"检查音频文件: {audio_path}",f"target_sample_rate:{target_sample_rate},target_channels:{target_channels}"):
            try:
                # 使用wave模块检查基本信息
                with wave.open(audio_path, 'rb') as wf:
                    framerate = wf.getframerate()
                    nchannels = wf.getnchannels()
                    self.logger.trace(f"当前音频参数 - 采样率: {framerate}Hz, 声道数: {nchannels}")
                    
                    # 如果已经是标准格式，直接返回原路径
                    if framerate == target_sample_rate and nchannels == target_channels:
                        self.logger.trace("音频格式符合要求，无需转换。")
                        return audio_path
            except Exception as e:
                self.logger.trace(f"无法用wave模块打开文件，将使用Pydub进行转换: {e}")
            
            # 使用Pydub进行格式转换
            self.logger.trace("音频格式不符合要求，开始转换...")
            audio = AudioSegment.from_file(audio_path)
            # 设置目标格式
            audio = audio.set_frame_rate(target_sample_rate).set_channels(target_channels)
            # 构建新文件名
            base, ext = os.path.splitext(audio_path)
            processed_audio_path = f"{base}_processed_16k_mono.wav"
            # 导出为标准WAV
            audio.export(processed_audio_path, format="wav")
            self.logger.trace(f"音频已转换并保存至: {processed_audio_path}")
        return processed_audio_path

    def split_audio_on_silence(self, audio_path, output_dir="temp_chunks", 
                                min_silence_len=800, silence_thresh=-40, keep_silence=300):
        """
        在静默点处将长音频分割成多个小片段。
        
        Args:
            audio_path (str): 输入音频文件路径。
            output_dir (str): 临时片段输出目录。
            min_silence_len (int): 被视为静默的最小持续时间（毫秒）。
            silence_thresh (int): 静默的音量阈值（dBFS）。
            keep_silence (int): 在每个片段前后保留的静默时长（毫秒）。
            
        Returns:
            list: 包含字典的列表，每个字典包含片段信息（路径、开始时间、结束时间）。
        """
        self.logger.trace("开始静默分割音频...")
        audio = AudioSegment.from_file(audio_path)
        total_duration = len(audio)
        self.logger.trace(f"音频总时长: {total_duration/1000:.2f} 秒")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        

        # 示例：将音频按固定30秒长度切分（假设 audio 是已加载的 AudioSegment 对象）
        chunk_length_ms = 30000  # 30秒
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        
        
        # 使用pydub的split_on_silence方法进行分割
        # chunks = split_on_silence(audio, 
        #                           min_silence_len=min_silence_len,
        #                           silence_thresh=silence_thresh, 
        #                           keep_silence=keep_silence)
        
        self.logger.trace(f"共检测到 {len(chunks)} 个静默分割点，得到 {len(chunks)} 个音频片段。")
        
        segments_info = []
        current_start = 0  # 当前片段在原始音频中的开始时间（毫秒）
        
        for i, chunk in enumerate(chunks):
            chunk_duration = len(chunk)
            chunk_end = current_start + chunk_duration
            
            # 跳过时长过短的片段（可能是无效静默）
            if chunk_duration < 500:  # 小于0.5秒
                self.logger.trace(f"跳过过短片段 {i} (时长: {chunk_duration}ms)")
                current_start = chunk_end
                continue
                
            # 导出片段
            chunk_filename = os.path.join(output_dir, f"chunk_{i:05d}.wav")
            chunk.export(chunk_filename, format="wav")
            
            segments_info.append({
                'path': chunk_filename,
                'start_ms': current_start,
                'end_ms': chunk_end,
                'duration_ms': chunk_duration
            })
            
            current_start = chunk_end
        
        # 打印分割结果概览
        for seg in segments_info:
            self.logger.trace(f"片段: {os.path.basename(seg['path'])}, "
                  f"开始: {seg['start_ms']/1000:.2f}s, "
                  f"时长: {seg['duration_ms']/1000:.2f}s")
        
        return segments_info

    def transcribe_segment(self, segment_info):
        """
        转录单个音频片段。
        
        Args:
            segment_info (dict): 包含片段信息的字典。
            
        Returns:
            dict: 包含转录结果和元数据的字典。
        """
        segment_path = segment_info['path']
        segment_start_sec = segment_info['start_ms'] / 1000.0  # 转换为秒，用于调整时间戳
        
        try:
            wf = wave.open(segment_path, 'rb')
            # 检查音频格式是否符合Vosk要求
            if wf.getframerate() != 16000 or wf.getnchannels() != 1:
                return {
                    'status': 'error',
                    'segment_info': segment_info,
                    'error': f"音频格式错误。期望 16000Hz 单声道，实际得到 {wf.getframerate()}Hz, {wf.getnchannels()}声道。"
                }
            
            # 为当前片段创建一个新的识别器实例
            recognizer = KaldiRecognizer(self.model, wf.getframerate())
            recognizer.SetWords(True)  # 启用单词级时间戳
            
            # 读取音频数据并进行识别
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result_json = recognizer.Result()
                    result_dict = json.loads(result_json)
                    results.append(result_dict)
            
            # 获取最终结果
            final_result_json = recognizer.FinalResult()
            final_result_dict = json.loads(final_result_json)
            results.append(final_result_dict)
            
            wf.close()
            
            # 处理识别结果，调整时间戳
            segments_with_adjusted_timestamps = []
            for result in results:
                if 'result' in result:
                    for word_info in result['result']:
                        # 将片段内相对时间戳调整为在原始音频中的绝对时间戳
                        adjusted_word_info = {
                            'word': word_info['word'],
                            'start': word_info['start'] + segment_start_sec,
                            'end': word_info['end'] + segment_start_sec,
                            'conf': word_info.get('conf', 0)
                        }
                        segments_with_adjusted_timestamps.append(adjusted_word_info)
            
            return {
                'status': 'success',
                'segment_info': segment_info,
                'words': segments_with_adjusted_timestamps
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'segment_info': segment_info,
                'error': str(e)
            }

    def _transcribe_segment_wrapper(self, segment_info):
        """一个包装器，用于将结果安全地添加到全局列表。"""
        result = self.transcribe_segment(segment_info)
        
        # 使用锁来安全地修改共享的结果列表
        with self._results_lock:
            self.all_segments.append(result)
        
        return result

    def process_long_audio(self, audio_path, output_json="final_transcription.json", output_txt="final_transcription.txt"):
        """
        处理长音频文件的主函数。
        
        Args:
            audio_path (str): 输入音频文件路径。
            output_json (str): JSON输出文件路径。
            output_txt (str): 纯文本输出文件路径。
            
        Returns:
            dict: 最终的转录结果。
        """
        # 1. 检查并预处理音频
        self.logger.update_target(f"处理文件{audio_path}",f"json_path:{output_json},txt_path:{output_txt}")
        processed_audio_path = self.check_and_preprocess_audio(audio_path)
        
        # 2. 静默分割音频
        segments_info = self.split_audio_on_silence(processed_audio_path,Path(processed_audio_path).parent/"segments")
        
        if not segments_info:
            raise Exception("音频分割失败，未得到任何有效片段。")
        
        self.logger.trace(f"\n开始使用 {self.max_workers} 个线程进行并行转录...",update_time_type=UpdateTimeType.STAGE)
        
        # 3. 使用线程池并行处理每个片段
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_segment = {executor.submit(self._transcribe_segment_wrapper, seg_info): seg_info for seg_info in segments_info}
            
            # 处理完成的任务，实时显示进度
            completed_count = 0
            for future in as_completed(future_to_segment):
                seg_info = future_to_segment[future]
                try:
                    result = future.result()
                    completed_count += 1
                    if result['status'] == 'success':
                        self.logger.trace(f"进度: {completed_count}/{len(segments_info)} - 成功: {os.path.basename(seg_info['path'])} (识别到 {len(result['words'])} 个词)",update_time_type=UpdateTimeType.STEP)
                    else:
                        self.logger.trace(f"进度: {completed_count}/{len(segments_info)} - 失败: {os.path.basename(seg_info['path'])} - 错误: {result['error']}",update_time_type=UpdateTimeType.STEP)
                except Exception as e:
                    self.logger.trace(f"处理片段 {seg_info['path']} 时发生异常: {e}",update_time_type=UpdateTimeType.STEP)
                    completed_count += 1
        
        # 4. 汇总和整理所有结果
        self.logger.trace("\n所有片段处理完成，开始汇总最终结果...",update_time_type=UpdateTimeType.STAGE)
        
        # 收集所有成功的单词
        all_words = []
        for segment_result in self.all_segments:
            if segment_result['status'] == 'success' and segment_result['words']:
                all_words.extend(segment_result['words'])
        
        # 按开始时间排序
        all_words.sort(key=lambda x: x['start'])
        
        # 将单词列表合并成段落/句子（这里采用简单的基于时间间隔的合并）
        merged_segments = []
        current_segment = {'text': '', 'start': None, 'end': None, 'words': []}
        word_gap_threshold = 1.0  # 如果单词间隔超过1秒，则开始新段落
        
        for word in all_words:
            if current_segment['start'] is None:
                # 第一个词
                current_segment['start'] = word['start']
                current_segment['end'] = word['end']
                current_segment['text'] = word['word']
                current_segment['words'] = [word]
            else:
                # 检查与上一个词的时间间隔
                if word['start'] - current_segment['end'] > word_gap_threshold:
                    # 时间间隔大，保存当前段落，开始新段落
                    merged_segments.append(current_segment)
                    current_segment = {'text': word['word'], 'start': word['start'], 'end': word['end'], 'words': [word]}
                else:
                    # 时间间隔小，合并到当前段落
                    current_segment['text'] += ' ' + word['word']
                    current_segment['end'] = word['end']
                    current_segment['words'].append(word)
        
        # 不要忘记最后一个段落
        if current_segment['text']:
            merged_segments.append(current_segment)
        
        # 构建最终结果字典
        final_result = {
            'metadata': {
                'source_audio': audio_path,
                'total_processing_time': None,  # 可以添加计时逻辑
                'total_segments_processed': len(segments_info),
                'successful_segments': len([r for r in self.all_segments if r['status'] == 'success']),
                'total_words_recognized': len(all_words),
                'model_used': os.path.basename(self.model_path)
            },
            'segments': merged_segments
        }
        
        # 5. 保存结果
        # 保存为JSON（包含所有详细信息）
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        self.logger.trace(f"详细结果已保存至: {output_json}")
        
        # 保存为易读的TXT文件
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write("音频转录结果\n")
            f.write("=" * 50 + "\n\n")
            for i, seg in enumerate(merged_segments):
                start_time = f"{int(seg['start']//60):02d}:{seg['start']%60:06.3f}"
                end_time = f"{int(seg['end']//60):02d}:{seg['end']%60:06.3f}"
                f.write(f"[{start_time} - {end_time}] {seg['text']}\n")
        self.logger.trace(f"纯文本结果已保存至: {output_txt}")
        
        # 6. 清理临时片段文件（可选）
        self.logger.trace("正在清理临时文件...")
        for seg_info in segments_info:
            try:
                os.remove(seg_info['path'])
            except:
                pass
        try:
            os.rmdir("temp_chunks")
        except:
            pass
        
        self.logger.trace("处理完成！")
        return final_result




# 使用示例
if __name__ == "__main__":
    # 配置参数
    model_path =r"D:\ai_model\vosk-model-cn-0.22"  # 替换为您的模型路径，例如 "./vosk-model-small-cn-0.15"
    input_audio =r"F:\知命\郑师兄_算卦.wav"     # 替换为您的长音频文件路径
    json_path = Path(input_audio).with_suffix(".json")
    txt_path=json_path.with_suffix(".txt")
    # 创建转录器实例
    transcriber = VoskBatchTranscriber(model_path, max_workers=8)
    
    # 开始处理
    result = transcriber.process_long_audio(input_audio,json_path,txt_path)
    logger=logger_helper(input_audio)
    # 打印一些统计信息
    logger.trace(f"\n=== 处理摘要 ===")
    logger.trace(f"源文件: {result['metadata']['source_audio']}")
    logger.trace(f"处理片段数: {result['metadata']['total_segments_processed']}")
    logger.trace(f"成功片段数: {result['metadata']['successful_segments']}")
    logger.trace(f"识别总词数: {result['metadata']['total_words_recognized']}")
    logger.trace(f"输出段落数: {len(result['segments'])}")