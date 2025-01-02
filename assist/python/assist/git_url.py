import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from base.file_tools import detect_encoding

def get_repo_urls(root_dir):
    urls = {}

    # 编译正则表达式，避免每次循环都重新编译
    remote_regex = re.compile(r'^\s*url\s*=\s*(.*)$', re.MULTILINE)

    # 遍历指定目录及其所有子目录
    for root, dirs, files in os.walk(root_dir):
        # 检查是否存在.git目录
        git_config_path = os.path.join(root, '.git', 'config')
        if os.path.exists(git_config_path) and os.path.isfile(git_config_path):
            try:
                # 读取配置文件
                encoding = detect_encoding(git_config_path)
                with open(git_config_path, 'r', encoding=encoding) as config_file:
                    content = config_file.read()

                # 解析配置文件以提取url
                match = remote_regex.search(content)
                if match:
                    url = match.group(1).strip()
                    urls[root] = url
                    
                    # 移除子目录，避免进一步遍历
                    dirs[:] = []
                    
            except Exception as e:
                print(f"Error reading {git_config_path}: {e}")
    return urls

# 使用函数
root_directory = r"F:\3rd_repositories"
repo_urls = get_repo_urls(root_directory)
for key, url in repo_urls.items():
    print(f"{key}, {url}")