import requests
import json
import time
from urllib.parse import urlencode
from pathlib import Path
import signal
from typing import Optional
import os
from base.com_log import global_logger,UpdateTimeType
from base.except_tools import except_stack
from base.com_exe_path import exe_path_from_environment
import subprocess
def is_aria2_running(rpc_url='http://localhost:6800/jsonrpc'):
    """检查 Aria2 RPC 服务是否已在运行且可响应"""
    try:
        response = requests.post(rpc_url, json={"jsonrpc": "2.0", "id": "check", "method": "aria2.getVersion"})
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

def smart_start_aria2(conf_path):
    """
    智能启动 Aria2 服务。
    如果服务已运行，则直接返回 None。
    如果未运行，则启动新进程并返回 Popen 对象。
    """
    with global_logger().raii_target("查找aria2服务",conf_path) as logger:

        if is_aria2_running():
            logger.trace("正在运行","无需重复启动。")
            return None
        else:
            logger.trace("未运行","正在启动...")
            return start_aria2_service(conf_path)
def start_aria2_service(conf_path: str, aria2c_executable: str = 'aria2c.exe') -> Optional[subprocess.Popen]:
    
    with global_logger().raii_target("开启aria2服务",conf_path) as logger:

        
        """
        启动 Aria2 RPC 服务进程。
        
        Args:
            conf_path (str): aria2.conf 配置文件的完整路径。
            aria2c_executable (str): aria2c 可执行文件的路径或命令。默认为 'aria2c'（假设已在系统PATH中）。
        
        Returns:
            Optional[subprocess.Popen]: 如果启动成功，返回 Popen 对象，用于后续管理进程；失败则返回 None。
        """
        # 1. 检查配置文件是否存在
        if not os.path.isfile(conf_path):
            logger.error("失败",f"Aria2 配置文件不存在: {conf_path}")
            return None
        aria_path=exe_path_from_environment(aria2c_executable)
        # 2. 构建启动命令
        # -D 参数让 Aria2 在后台（守护进程）模式运行
        command = [
            aria_path,
            f'--conf-path={conf_path}',
            '-D'  # 后台运行
        ]
        
        try:
            # 3. 使用 subprocess.Popen 启动进程
            # 将标准输出和标准错误重定向到 subprocess.DEVNULL，避免输出干扰控制台
            # 也可以考虑重定向到日志文件，例如：open('aria2.log', 'w')
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if os.name == 'posix' else None  # 用于Unix系统，创建新的进程组
            )
            logger.trace(f"启动命令已执行: {' '.join(command)}")
            
            # 4. 短暂等待，让服务有时间初始化
            time.sleep(3)
            
            # 5. 检查进程是否仍在运行
            if process.poll() is None:
                logger.trace("成功",f"进程PID: {process.pid}")
                return process
            else:
                # 如果进程已经结束，poll()返回退出码，说明启动失败
                return_code = process.poll()
                logger.error("启动失败",f"进程已退出，返回码: {return_code}")
                # 可以尝试获取错误信息（如果未重定向stderr，则需从PIPE读取）
                # 但此处我们重定向到了DEVNULL，所以需要依赖日志和配置文件检查
                return None

        except FileNotFoundError:
            logger.error("失败",f"未找到 aria2c 可执行文件 '{aria2c_executable}'。请确保 Aria2 已安装并正确配置在系统PATH环境变量中。")
            return None
        except Exception as e:
            logger.error("失败",f"启动 Aria2 服务时发生未知错误: {e}\n{except_stack()}")
            return None

def stop_aria2_service(process: subprocess.Popen) -> bool:
    """
    停止由 `start_aria2_service` 启动的 Aria2 服务进程。
    
    Args:
        process (subprocess.Popen): 要停止的进程对象。
    
    Returns:
        bool: 成功停止返回 True，否则返回 False。
    """
    
    with global_logger().raii_target("关闭aria2服务") as logger:
        try:
            if process and process.poll() is None:  # 检查进程是否仍在运行
                # 发送终止信号。使用进程组，确保终止整个进程树（特别是对于Unix系统）
                if os.name == 'posix':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    # 对于Windows
                    process.terminate()
                
                # 等待进程结束
                process.wait(timeout=10)
                logger.info("成功","Aria2 服务已停止。")
                return True
        except Exception as e:
            logger.error("失败",f"停止 Aria2 服务时发生错误: {e}")
            try:
                process.kill()  # 如果terminate无效，强制杀死
            except:
                pass
    return False

class Aria2RPC:
    def __init__(self, rpc_url='http://localhost:6800/jsonrpc', rpc_secret=None,aria2_config_path:str = None):
        self.rpc_url = rpc_url
        self.secret = rpc_secret
        self.aria2_process = smart_start_aria2(aria2_config_path)
    @property
    def is_aria2_running(self):
        return is_aria2_running()
    
    # 在程序退出前，如果您希望停止自己启动的服务，可以取消下面行的注释
    def close_aria2(self):
        """关闭Aria2进程"""
        if self.is_aria2_running:
            stop_aria2_service(self.aria2_process)
    
    def _call(self, method, params=None):
        """调用RPC方法的内部函数"""
        if params is None:
            params = []
        # 如果设置了密钥，将其添加到参数前面
        if self.secret:
            params = [f"token:{self.secret}"] + params
            
        payload = {
            'jsonrpc': '2.0',
            'id': '1',
            'method': method,
            'params': params
        }
        
        try:
            response = requests.post(self.rpc_url, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            global_logger().trace(f"RPC调用失败: {e}")
            return None

    def add_uri(self, uris, options=None):
        """添加下载任务"""
        if options is None:
            options = {}
        if not isinstance(uris, list):
            uris = [uris]
        return self._call('aria2.addUri', [uris, options])

    def tell_status(self, gid):
        """查询任务状态"""
        return self._call('aria2.tellStatus', [gid])
    
    def get_global_stat(self):
        """获取全局统计信息"""
        return self._call('aria2.getGlobalStat')
def main(urls:str|list[str],dest_paths:str|list[str],aria2_config_path:str):
    # 要下载的文件列表（可以是HTTP链接或磁力链接）
    if isinstance(urls,str):
        urls = [urls]
    if isinstance(dest_paths,str):
        dest_paths = [dest_paths]

    if not urls or not dest_paths: return
    def _dest_option(dest_path:str):
        cur_path=Path(dest_path)
        cur_dir=cur_path.parent
        result={"out": cur_path.name}
        if cur_dir.is_dir():
            result["dir"]=str(cur_dir)
        return result
    tasks=[([url],_dest_option(dest_path)) for url,dest_path in zip(urls,dest_paths)]
    if not tasks: 
        return
    global_logger().update_time(UpdateTimeType.ALL)

    # 情况1：没有设置 rpc-secret
    aria2 = Aria2RPC(aria2_config_path=aria2_config_path) # 使用默认的 http://localhost:6800/jsonrpc

    # # 情况2：设置了 rpc-secret
    # aria2 = Aria2RPC(rpc_secret='my_super_secret_token_123')

    # # 情况3：Aria2服务在另一台机器上，且设置了secret
    # aria2 = Aria2RPC(
    #     rpc_url='http://192.168.1.100:6800/jsonrpc', # 替换为您的Aria2服务器IP
    #     rpc_secret='my_super_secret_token_123'
    # )
    if not aria2.is_aria2_running:
        return "Aria2服务未启动"


    with global_logger().raii_target("添加aria2下载任务",f"共{len(tasks)}个") as logger:
        # 添加下载任务
        active_downloads = []
        for url,option in tasks:
            result = aria2.add_uri(url, options=option)  # 指定下载目录
            if result and 'result' in result:
                gid = result['result']  # 获取任务ID
                active_downloads.append(gid)
                logger.trace("成功",f"GID: {gid}",update_time_type=UpdateTimeType.STEP)
        logger.info("成功",update_time_type=UpdateTimeType.STAGE)
        
        # 监控下载进度
        with logger.raii_target("aria2下载",detail="监控下载进度") as inner_logger:
            while active_downloads:
                # 测试连接
                global_stat = aria2.get_global_stat()
                if global_stat and 'result' in global_stat:
                    stat = global_stat['result']
                    inner_logger.trace("任务状态",f"下载速度: {stat.get('downloadSpeed', '0')} B/s, 活跃任务数: {stat.get('numActive', '0')}")
                
                for gid in active_downloads[:]:  # 使用副本进行遍历
                    status = aria2.tell_status(gid)
                    if status and 'result' in status:
                        task_info = status['result']
                        inner_logger.trace(f"任务 {gid} 状态",f"{task_info['status']}, 进度: {task_info.get('completedLength', '0')}/{task_info.get('totalLength', '未知')}")
                        
                        # 如果任务完成、出错或停止，则从监控列表中移除
                        if task_info['status'] in ['complete', 'error', 'removed']:
                            inner_logger.info("完成",f"任务 {gid} 已完成或停止，状态: {task_info['status']}",update_time_type=UpdateTimeType.STAGE)
                            active_downloads.remove(gid)
                
                time.sleep(2)  # 每2秒检查一次
        
            inner_logger.trace("所有下载任务已完成！")
        
# 使用示例
if __name__ == "__main__":
    
    urls=["https://d.pcs.baidu.com/file/263546a2387d2c199f07bbb4e4009547?fid=2315822378-250528-716885982580256&dstime=1766032585&rt=sh&sign=FDtAERJoK-DCb740ccc5511e5e8fedcff06b081203-kFnSO%2BVnJKCeDoIR3c%2B6zLjkDt8%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=82413247433474667&dp-callid=0&r=642271081&vuk=1101719631688&file_type=0&clienttype=8&sh=1",
          ]
    dest_paths=[
        "汉字宫3.rar",
        ]
    aria2_config_path=r"F:\test\ubuntu_configure\assist\python\assist\aria2.conf"
    main(urls,dest_paths,aria2_config_path=aria2_config_path)
    
 
    
#aria2c --conf-path=/path/to/your/aria2.conf -D

"""
使用方法详解
1.单个文件下载时指定文件名

这是最直接的方法。在下载命令后添加 -o（小写字母 o）参数，紧跟你想命名的文件即可 。

bash
复制
aria2c -o "我的电子书.pdf" "https://example.com/path/to/a_complicated_filename.pdf"

2..批量下载时指定不同文件名

当你需要从文件列表批量下载，并希望为每个文件自定义名称时，方法也很简单：

创建一个文本文件（例如 url_list.txt），按以下格式编写内容：每一行先写文件链接，然后在下一行用 out=你的文件名.扩展名来指定该链接对应的文件名。注意：out所在行必须以空格或制表符开头​ 。

复制
https://cdn.example.com/videos/intro.mp4
    out=项目介绍视频.mp4
https://cdn.example.com/docs/spec.pdf
    out=产品规格说明书.pdf

使用 -i参数进行下载：

bash
复制
aria2c -i url_list.txt

Aria2 会根据列表中的设置自动下载并重命名文件。

"""