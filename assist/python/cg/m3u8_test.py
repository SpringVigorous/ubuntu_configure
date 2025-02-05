import os
import requests
import subprocess
from urllib.parse import urljoin

# 配置参数
m3u8_url = "https://video.gzfeice.cn/b7554d95vodtranscq1254019786/5296e01c1397757903358079695/voddrm.token.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9~eyJ0eXBlIjoiRHJtVG9rZW4iLCJhcHBJZCI6MTI1NDAxOTc4NiwiZmlsZUlkIjoiMTM5Nzc1NzkwMzM1ODA3OTY5NSIsImN1cnJlbnRUaW1lU3RhbXAiOjAsImV4cGlyZVRpbWVTdGFtcCI6MjE0NzQ4MzY0NywicmFuZG9tIjowLCJvdmVybGF5S2V5IjoiIiwib3ZlcmxheUl2IjoiIiwiY2lwaGVyZWRPdmVybGF5S2V5IjoiNmM1OGI3YThiMWRmODA5NWM2NThmNDUyNDYxMmZkZWEwOWRlMGZmMTVmZDU1MmZlNmJkYWFjYzBjMGE3M2ExNGVlZjk2ZWVjOThiNTNjYTg0Y2U3NmNkYzcyYjQwZWViYmQ5ODM4N2FkMjMxNzE1MjNiMTI4MmYxYThlY2Y3YTU4ZjY3MDJhZmY5YzIzNGE1ZDA4YjJiNGIzYjM2MmNlM2FkZmFkMTAwOWY2NzBkMzNmYWNhOWI3MGUzNzhlY2IxZGM1MDQyMzZmYzFlZjY4ZmU0OTk3ZjdiYzZkMWI0MmMzMjQzOGEyZmNmMzIxZWQzOTY5MGUzNzU1MjM0NGZiMCIsImNpcGhlcmVkT3ZlcmxheUl2IjoiMjZjYzdiZDg4ZmQ2NjRmYjVlNDQyZjIwN2E3YThhMTk2NDRlMmQ5MDVlZmVlNjZhMmZlNTlmNGRjZGQyYjdmYWQxNzI4MjBiZThiODlhOTc0MjU2OTNjZTE1YzA3MDU5NGM2ZWU3M2EzMDI3ODk3Y2RhMjE0YTkzZmQ5OWQ1N2I3NDFmY2VkMDc1MDk2N2JkMDhmMzVlYjBlODFmZjgxNjYwYjg5MmFkZjI4YmQ0ZDQwNjQxZjc1OTg5ZWRlYmNkYjM1NDU3MDA5MGM5NjQzNTcxOGJkZWM2Y2UzZjI4YWVkZGI2ZmM2OWFlMzhhOTVmYzdkMGRiNDA3NDY1MWU4ZiIsImtleUlkIjoxLCJzdHJpY3RNb2RlIjowLCJwZXJzaXN0ZW50IjoiIiwicmVudGFsRHVyYXRpb24iOjAsImZvcmNlTDFUcmFja1R5cGVzIjpudWxsfQ~Evr4YUvlcwsHH_1xkr7WbKdXbVPD-qvelazjBW1R9iM.video_1444917_2.m3u8?encdomain=cmv1"
output_dir = "downloaded_ts_files"
output_mp4 = "output.mp4"

# 创建下载目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 下载m3u8文件
response = requests.get(m3u8_url)
m3u8_content = response.text
m3u8_file = os.path.join(output_dir, "playlist.m3u8")
with open(m3u8_file, "w") as f:
    f.write(m3u8_content)

# 解析m3u8文件，提取.ts文件和密钥信息
ts_files = []
key_url = None
iv_hex = None
for line in m3u8_content.splitlines():
    if line.startswith("#EXT-X-KEY:"):
        key_info = line.split("URI=\"")[1].split("\"")[0]
        key_url = key_info
        iv_hex = line.split("IV=0x")[1].split(",")[0] if "IV=0x" in line else None
    elif line.endswith(".ts"):
        ts_files.append(line)

# 下载.ts文件
for ts_file in ts_files:
    ts_url = urljoin(m3u8_url, ts_file)
    ts_path = os.path.join(output_dir, ts_file.split("/")[-1])
    response = requests.get(ts_url)
    with open(ts_path, "wb") as f:
        f.write(response.content)

# 下载解密密钥
if key_url:
    key_response = requests.get(key_url)
    key_path = os.path.join(output_dir, "key.bin")
    with open(key_path, "wb") as f:
        f.write(key_response.content)

# 使用ffmpeg解密并合并.ts文件
ts_list_file = os.path.join(output_dir, "ts_list.txt")
with open(ts_list_file, "w") as f:
    for ts_file in ts_files:
        ts_path = os.path.join(output_dir, ts_file.split("/")[-1])
        f.write(f"file '{ts_path}'\n")

ffmpeg_command = [
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", ts_list_file,
    "-c", "copy",
    "-decryption_key", key_path if key_url else "none",
    "-iv", iv_hex if iv_hex else "none",
    output_mp4
]

subprocess.run(ffmpeg_command)

print(f"视频已合并为 {output_mp4}")