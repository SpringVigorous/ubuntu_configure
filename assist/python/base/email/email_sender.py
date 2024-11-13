import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import json
from enum import Enum

import sys
import os



# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(__file__))
# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

from  com_log import  logger_helper
from  com_decorator import exception_decorator
from file_tools import detect_encoding
from string_tools import exe_dir
    


# 定义枚举变量，用于标识不同的邮箱服务提供商
class EmailType(Enum):
    QQ = 'qq'
    OUTLOOK = 'outlook'
    ALIYUN = 'aliyun'
    SOHU = 'sohu'
    
    @classmethod
    def from_string(cls, value):
        """从字符串值创建枚举实例"""
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"无效的值: {value}")

class EmailSender:
    def __init__(self, sender_email:str, password:str):
        """
        初始化 EmailSender 实例
        
        :param sender_email: 发件人的邮箱地址
        :param password: 发件人的邮箱密码或授权码
        """
        self.email = sender_email
        self.password = password
        self.email_type, self.smtp_server, self.smtp_port = self._get_smtp_config(sender_email)

    def _get_smtp_config(self, email:str):
        """根据发件人邮箱获取 SMTP 配置"""
        if not email:
            raise ValueError("发件人邮箱不能为空")
        domain = email.split('@')[1].split(".")[0]
        config = self._load_config().get(domain)
        if not config:
            raise ValueError(f"不支持的邮箱域名: {domain}")
        return EmailType.from_string(domain), config['smtp_server'], config['smtp_port']

    def _load_config(self):
        """加载 SMTP 配置文件"""
        file_path = os.path.join(exe_dir(__file__),'email_config.json')
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            return json.load(file)

    @property
    def is_qq(self):
        """判断是否为 QQ 邮箱"""
        return self.email_type == EmailType.QQ

    @property
    def is_outlook(self):
        """判断是否为 Outlook 邮箱"""
        return self.email_type == EmailType.OUTLOOK

    @property
    def is_aliyun(self):
        """判断是否为 Aliyun 邮箱"""
        return self.email_type == EmailType.ALIYUN

    @property
    def is_sohu(self):
        """判断是否为 Sohu 邮箱"""
        return self.email_type == EmailType.SOHU
        """
        'plain':

        用于发送纯文本消息。
        适用于简单的文本内容。
        'html':

        用于发送 HTML 格式的富文本消息。
        适用于带有格式的文本内容，如加粗、斜体、链接等。
        'xml':

        用于发送 XML 格式的数据。
        适用于发送结构化的数据内容。
        'rtf':

        用于发送 RTF 格式的富文本消息。
        适用于发送带有格式的文本内容，类似于 Word 文档。
        """
    @exception_decorator()
    def send_email(self, receiver_email: str | list, subject:str, body:str,body_type:str='plain', attachments:str|list=None, body_files:str|list=None):
        """
        发送邮件
        
        :param receiver_email: 收件人邮箱地址，可以是单个地址或地址列表
        :param subject: 邮件主题
        :param body: 邮件正文
        :param attachments: 附件路径列表
        :param body_files: 正文文件路径列表
        """
        
        
        recivers=', '.join(receiver_email) if type(receiver_email) is list else receiver_email
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = recivers
        msg['Subject'] = subject

        email_helper=logger_helper(f"{self.email}->{recivers}","发送邮件")
        
        attachment_list=attachments if type(attachments)==list else [attachments] if attachments is not None else []
        bodyfiles_list=body_files if type(body_files)==list else [body_files] if body_files is not None else []
        
        # 添加正文
        msg.attach(MIMEText(body, body_type))
        
        if bodyfiles_list:
            for body_file in bodyfiles_list:
                if not body_file or not os.path.exists(body_file):
                    continue
                encoding= detect_encoding(body_file)
                with open(body_file, 'r', encoding=encoding) as file:
                    file_body = file.read()
                    msg.attach(MIMEText(file_body, 'plain'))
        
        # 添加附件
        if attachment_list:
            for attachment in attachment_list:
                if not attachment or not os.path.exists(attachment):
                    continue
                with open(attachment, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=attachment)
                    part['Content-Disposition'] = f'attachment; filename="{attachment}"'
                    msg.attach(part)

        try:
            # 连接到服务器
            connect_fun = smtplib.SMTP_SSL if self.is_qq else smtplib.SMTP
            self.server = connect_fun(self.smtp_server, self.smtp_port)

            if self.is_outlook:
                self.server.starttls()  # 启用 TLS 加密

            self.server.login(self.email, self.password)
            
            # 发送邮件

            
            self.server.sendmail(self.email, receiver_email, msg.as_string())
            
            msg_info=f"邮件主题：{subject}\n收件人：{recivers}\n正文：{body}\n附件：{attachments}\n正文文件：{body_files}"
            
            email_helper.info("成功",msg_info,True)
        except Exception as e:
            email_helper.error("失败",f"原因：{e}",True)

        finally:
            if self.server:
                self.server.quit()

def test():
    # 使用 QQ 邮箱发送邮件
    sender_email = '960902471@qq.com'
    password = 'txxbbjkizzhabdjg1'
    # receiver_email = ['1107917658@qq.com',"spring_flourish@outlook.com","spring_flourish@aliyun.com"]
    receiver_email = ['1107917658@qq.com']
    subject = '邮件主题'
    body = 'dfadsfasd'
    attachments = ['F:/test/ubuntu_configure/assist/python/logs/redbook_threads-trace.log']
    body_files = ['F:/test/ubuntu_configure/assist/python/logs/redbook_threads-trace.log']
    


    email_sender = EmailSender(sender_email, password)
    email_sender.send_email(receiver_email, subject, body, 'plain',attachments, body_files)



# 示例使用
if __name__ == "__main__":
    test()