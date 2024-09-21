from pydub import AudioSegment
import speech_recognition as sr
import os

dir_path=r"F:\教程\C++\双笙子佯谬\Zeno"
file_name=r" 【Zeno】Python脚本赋能Taichi生成“福特球”分形图案（第十期）.mp4"

# 读歌音频攻件
audio =AudioSegment.from_file(os.path.join(dir_path,file_name),format="mp4")
# 创建一个语音识别器对象
recognizer =sr.Recognizer()
# 将音频内容转换为攻本
text = recognizer.recognize_google(audio)
#将文本内容写入到字幕文件中
with open("subtitle.srt","w")as file:
    file.write(text)