from vosk import Model, KaldiRecognizer
import wave
from pathlib import Path
from base import exception_decorator,logger_helper,UpdateTimeType,read_from_json,write_to_json,convert_seconds_to_time_str,generate_srt


import json
import math
import pandas as pd



def recognize_sound(wav_file:wave.Wave_read,rec:KaldiRecognizer,frame_count:int=4000)->list[dict]:
    logger=logger_helper("音频->文本")
    result_lst=[]
    cur_times=0
    start_times=0
    total_frames = wav_file.getnframes()
    count:int=math.ceil(float(total_frames)/frame_count)
    #调试窗口 快速退出
    # open(Path(r"F:\知命\郑师兄_算卦.wav").with_suffix(".json"), "w", encoding="utf-8").write(f'[{",\n".join(result_lst)}]')
    
    while True:
        with logger.raii_target(detail=f"{start_times}->第{cur_times}段,进度:{float(cur_times)/count:.2%}"):
            try:
                data = wav_file.readframes(frame_count)  # 每次读取 4000 帧
                cur_times+=1
                if len(data) == 0:
                    break  # 音频读取完毕
                if rec.AcceptWaveform(data):
                    # 输出临时识别结果（每段音频的完整句子）
                    result = rec.Result()
                    if not result:  # 忽略空结果
                        continue
                    result=handle_recognize_result(json.loads(result))
                    if not result:  # 忽略空结果
                        continue
                    start_times=cur_times
                    logger.trace("识别结果",result,update_time_type=UpdateTimeType.STEP)
                    result_lst.append(result)  # 累加结果
            except Exception as e:
                logger.error("异常",f"{e}",update_time_type=UpdateTimeType.STEP)
                continue
    logger.info("识别完成",update_time_type=UpdateTimeType.STAGE)
    # 5. 获取最后一段识别结果
    final_text = rec.FinalResult()
    if final_text:
        result=handle_recognize_result(json.loads(final_text))
        result_lst.append(result)
    
    return list(filter(lambda x:x and x["text"],result_lst))


@exception_decorator(error_state=False)
def handle_recognize_result(result:dict):
    if not result: return
    dest={"text":result['text']}
    if 'result' not in result:
        return dest
    items=result['result']
    if items: 
        try:
            dest["start"]=items[0]['start']
            dest["end"]=items[-1]['end']
        except:
            pass
    return dest

@exception_decorator(error_state=False)
def handle_result(results:list[dict],xlsx_path:str):
    df= pd.DataFrame(results)
    df["start"]=df["start"].apply(convert_seconds_to_time_str)
    df["end"]=df["end"].apply(convert_seconds_to_time_str)
    df.to_excel(xlsx_path)
    
    # .srt文件
    srt_data=[(x["start"],x["end"],x["text"]) for x in data]
    generate_srt(srt_data,Path(xlsx_path).with_suffix(".srt"),time_unit="s")
    
    pass

def main(wave_path:str)->str:
    logger=logger_helper("识别音频",wave_path)
    
    # 1. 加载模型（替换为你的模型路径）
    model = Model(r"D:\ai_model\vosk-model-cn-0.22")

    # 2. 打开音频文件（需是 16000Hz 单声道 PCM 格式）
    wav_file = wave.open(wave_path, "rb")

    # 3. 初始化识别器
    rec = KaldiRecognizer(model, wav_file.getframerate())
    rec.SetWords(True)


    """
    # 获取采样率（每秒帧数）
    framerate = wf.getframerate()  # 示例中为 16000
    # 获取总帧数
    total_frames = wf.getnframes()
    # 获取声道数、位深等（可选）
    nchannels = wf.getnchannels()
    sampwidth = wf.getsampwidth()  # 位深（字节数，16位=2字节）
    t = 2.5  # 目标时间（秒）
    target_frame = int(t * framerate)  # 2.5 × 16000 = 40000 帧
    # 跳转到目标帧数
    wf.setpos(target_frame)
    """

    # 4. 读取音频并识别
    result_data= recognize_sound(wav_file=wav_file, rec=rec,frame_count=16000)
    org_path=Path(wav_file)
    json_path=org_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
         json.dump(result_data,f,ensure_ascii=False,indent=4)

    #5. 识别结果的处理
    handle_result(result_data,org_path.with_suffix(".xlsx"))

    
    
if __name__ == "__main__":
    wave_path=Path(r"F:\知命\郑师兄_算卦.wav")
    main(wave_path)
    exit()
    
    json_path=wave_path.with_suffix(".json")
    data= read_from_json(json_path,encoding="utf-8-sig")
    data=list(filter(lambda x:x and x["text"],data))

    # with open(json_path, "w", encoding="utf-8-sig") as f:
    #     json.dump(data,f,ensure_ascii=False,indent=4)
    # handle_result(data,wave_path.with_suffix(".xlsx"))
    

    
    