import os

def get_repo_urls(root_dir):
    urls = {}

    # 遍历指定目录及其所有子目录
    for root, dirs, files in os.walk(root_dir):
        # 检查是否存在.git目录
        git_config_path = os.path.join(root, '.git', 'config')
        if os.path.exists(git_config_path) and os.path.isfile(git_config_path):
            # 读取配置文件
            with open(git_config_path, 'r') as config_file:
                content = config_file.read()

            # 解析配置文件以提取url
            url = extract_remote_url(content)
            if url is not None:
                # urls[os.path.basename(root)]=url
                urls[root]=url
    return urls

def extract_remote_url(config_content):
    # .git/config 文件中远程库URL的格式通常是：
    # [remote "origin"]
    #     url = https://github.com/user/repo.git
    # 因此，可以使用正则表达式或其他解析方法来提取url
    import re
    pattern = r'^\s*url\s*=.*'
    remote_regex = re.compile(pattern, re.MULTILINE)

    matches = remote_regex.findall(config_content)
    if matches:
        # 取第一个远程URL作为默认（通常'origin'是默认的远程）,子模块先不用管
        url_match = matches[0].split('=', 1)[1].strip()
        return url_match
    else:
        return None

# 使用函数
root_directory = f"F:/test/"
repo_urls = get_repo_urls(root_directory)
for key,url in repo_urls.items():
    print(f"{key}, {url}")