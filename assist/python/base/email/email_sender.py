import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import json
from enum import Enum
from email.header import Header
import sys
import os
from pathlib import Path




from  com_log import  logger_helper
from  com_decorator import exception_decorator
from base.file_tools import detect_encoding
from base.string_tools import exe_dir,hash_text
from base.path_tools import is_image_file
    
from PIL import Image
import os
from enum import IntFlag, auto

class ImageMode(IntFlag):
    """图像类型位标志枚举，支持组合状态"""
    INSERT = auto()    # 自动分配值 1 (0b01)
    ATTACH = auto()    # 自动分配值 2 (0b10)
    INSERT_ATTACH = INSERT | ATTACH  # 组合状态，值=3 (0b11)

    # --- 功能方法 ---
    @property
    def can_insert(self) -> bool:
        return self & ImageMode.INSERT != 0  # 检查是否包含INSERT标志位

    @property
    def can_attach(self) -> bool:
        return self & ImageMode.ATTACH != 0  # 检查是否包含ATTACH标志位
    
    @property
    def is_insert_and_attach(self) -> bool:
        """是否同时包含插入和附件"""
        return self.can_insert() and self.can_attach()
    

    
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
    def send_email(self, receiver_email: str | list, subject:str, body:str,body_type:str='plain', attachments:str|list=None, body_files:str|list=None,image_mode:ImageMode=ImageMode.ATTACH):
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
        msg.attach(MIMEText(body, body_type,"utf-8"))
        
        if bodyfiles_list:
            for body_file in bodyfiles_list:
                if not body_file or not os.path.exists(body_file):
                    continue
                encoding= detect_encoding(body_file)
                with open(body_file, 'r', encoding=encoding) as file:
                    file_body = file.read()
                    msg.attach(MIMEText(file_body, 'plain',"utf-8"))
        
        # 添加附件
        if attachment_list:
            for attachment in attachment_list:
                if not attachment or not os.path.exists(attachment):
                    continue
                
                attachment_name = Path(attachment).name
                try:
                    with open(attachment, 'rb') as file:
                        data=file.read()
                        #若是图片,顺便添加到正文，即设置id
                        if is_image_file(attachment) and image_mode.can_insert:
                            
                            part = MIMEImage(data)
                            part.add_header('Content-ID', f'<{hash_text(attachment)}>')  # CID与HTML中一致
                            # part.add_header('Content-Disposition', 'inline', filename=attachment_name)  # 关键修改
                            #后续证明，没有什么用
                            # if image_as_attachment:
                            #     part.add_header('Content-Disposition', 'attachment', filename={attachment_name})  # 关键修改
                            msg.attach(part)
                            
                            #如果不作为附件，则直接返回，忽略后续的 添加附件
                            if not image_mode.can_attach:
                                continue

                        #保存为附件
                        part = MIMEApplication(data, Name=attachment_name)
                        part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
                        msg.attach(part)
                except Exception as e:
                    email_helper.error("添加附件失败",f"原因：{e}")
                

                    

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

def test_1():
    # 使用 QQ 邮箱发送邮件
    sender_email = '960902471@qq.com'
    password = 'txxbbjkizzhabdjg'
    # receiver_email = ['1107917658@qq.com',"spring_flourish@outlook.com","spring_flourish@aliyun.com"]
    receiver_email = ['1107917658@qq.com']
    subject = '测试图文混合内容'
    from base.root_config import worm_root
    

    
    cur_dir=worm_root/r"taobao\五味食养\images_prohibite"
    org_files=["微信图片_20250727225420_674.jpg",
        "微信图片_20250727225424_673.jpg",
        "微信图片_20250727225430_672.jpg",
        "微信图片_20250727225438_670.jpg",
        "微信图片_20250727225446_669.jpg",
        ]
    attachments = [os.path.join(cur_dir,file) for file in org_files]
    
    file_infos=[(os.path.join(cur_dir,file), file) for file in org_files]

#     html_content = """
#     <html>
#     <body>
#     <table style="border-collapse: collapse; width: auto;">
#         <tr>
#         <th style="text-align:center; border:1px solid black; padding:8px;">编号</th>
#         <th style="text-align:center; border:1px solid black; padding:8px;">描述</th>
#         <th style="text-align:center; border:1px solid black; padding:8px;">图片</th>
#         </tr>
#         {rows}
#     </table>
#     </body>
#     </html>
#     """.format(
#          rows="".join(
# f'<tr><td style="vertical-align:top;  border:1px solid black;padding:8px;width:auto;">{index+1}</td><td style="vertical-align:top;  border:1px solid black;padding:8px;width:auto;">{row[1]}</td><td style="vertical-align:center; border:1px solid black; padding:8px;width:auto;"><img src="cid:{hash_text(row[0])}" style="display:block;" ></td></tr>'
#             for index,row in enumerate(file_infos)
#         )
#     )

    
    
    from html_tools import HtmlHelper
    heads=["编号","描述","图片"]
    bodys=[
        [(index+1,0,"top"),(row[1],0,"top"),(hash_text(row[0]),1,"center")]
        for index,row in enumerate(file_infos)
    ]
    html_content = HtmlHelper.html_tab(heads,bodys)
    
    
    
    email_sender = EmailSender(sender_email, password)
    email_sender.send_email(receiver_email, subject, html_content, 'html',attachments)

# 示例使用
if __name__ == "__main__":
    # test()
    test_1()

