
import json

import sys
import os

# 获取项目根目录
project_root = os.path.dirname(__file__)
# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.append(project_root)


from email_sender import EmailSender

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(__file__))
# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.append(project_root)
from  com_decorator import exception_decorator
from string_tools import exe_dir

@exception_decorator()
def send_email(subject,body,body_type='plain',attachment_path:str|list=None,bodyfiles:str|list=None):
        """加载 SMTP 配置文件"""
        setting=None
        file_path = os.path.join(exe_dir(__file__),'setting.json')
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            setting= json.load(file)
        if setting is None:
            return
        
        sender=setting["sender"]
        
        sender_email=sender["email"]
        password=sender["password"]
        receiver_email=setting["receiver"]["email"]

    
        email_sender = EmailSender(sender_email, password)
        
        attachment_list=attachment_path if type(attachment_path)==list else [attachment_path] if attachment_path is not None else []
        bodyfiles_list=bodyfiles if type(bodyfiles)==list else [bodyfiles] if bodyfiles is not None else []
        
        email_sender.send_email(receiver_email, subject, body,body_type, attachment_list, bodyfiles_list)

    
    
    
    

if __name__ == '__main__':
    send_email('test subject','test body','C:\\Users\\Administrator\\Desktop\\test.txt')