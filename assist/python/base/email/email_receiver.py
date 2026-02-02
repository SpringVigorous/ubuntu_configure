import os
import time
import ssl

from imapclient import IMAPClient
from email.parser import BytesParser
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import os
import re




from  base.com_log import  logger_helper
import codecs


from OpenSSL import crypto  # 需要安装pyopenssl
from email import policy

from email.header import decode_header
from email.utils import parsedate_to_datetime
import quopri
import base64
import time
from datetime import datetime, timedelta
import chardet
import html2text

def html_to_text(html_content:str):
    """将 HTML 转换为格式清晰的纯文本"""
    converter = html2text.HTML2Text()
    converter.ignore_links = False    # 保留链接文本
    converter.body_width = 0         # 禁用自动换行
    converter.ul_item_mark = '-'      # 统一列表符号
    converter.ignore_images = True    # 忽略图片
    converter.single_line_break = True # 将单个 <br> 视为换行
    # 自定义处理规则（可选）
    converter.protect_links = True    # 保护链接结构
    # 处理非标准编码的 HTML
    # html = html_content.decode('gbk', errors='ignore')
    return converter.handle(html_content)

# # 示例使用
# html = """
# <h1>标题</h1>
# <p>正文 <a href="https://example.com">示例链接</a></p>
# <ul>
#     <li>项目1</li>
#     <li>项目2</li>
# </ul>
# """

# text = html_to_text(html)
# print(text)


def parse_email(raw_email):
    """解析邮件完整信息"""
    # print(raw_email)
    
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)
    
    # 初始化解析结果
    parsed = {
        'from': parse_header(msg.get('From', '')),
        'to': parse_header(msg.get('To', '')),
        'subject': parse_header(msg.get('Subject', '无主题')),
        'date': parse_date(msg.get('Date')),
        'text_body': '',
        'html_body': '',
        'attachments': []
    }
    
    # 递归解析邮件内容
    parsed.update(parse_content(msg))
    return parsed

def parse_content(part):
    """解析邮件内容部分"""
    result = {'text_body': '', 'html_body': '', 'attachments': []}
    logger=logger_helper("解析邮件内容")
    # 处理多部分邮件
    if part.is_multipart():
        for sub_part in part.iter_parts():
            content_type = sub_part.get_content_type()
            disposition = sub_part.get('Content-Disposition', '')
            
            if 'attachment' in disposition:
                result['attachments'].append({
                    'filename': parse_header(sub_part.get_filename()),
                    'content_type': content_type,
                    'size': len(sub_part.get_payload(decode=True))
                })
            else:
                sub_result = parse_content(sub_part)
                result['text_body'] += sub_result['text_body']
                result['html_body'] += sub_result['html_body']
                
    # 处理单部分邮件
    else:
        #decode=True 时，若是base64编码的，会自动解码
        payload = part.get_payload(decode=True)
        logger.update_target(detail=f"原始数据：{payload}")
        # logger.trace("开始解码")

        org_charset = part.get_content_charset()
        not_set_charset= org_charset is None or org_charset.strip() == ''
        charset='utf-8' if  not_set_charset else org_charset
        
        raw_data=None
        # 解码quoted-printable编码
        if part.get('Content-Transfer-Encoding', '') == 'quoted-printable':
            raw_data = quopri.decodestring(payload)
        # elif part.get('Content-Transfer-Encoding', '') == 'base64':
        #     raw_data = base64.b64decode(payload)
        else:
            raw_data = payload
        
        
        #尝试解码
        try:
            try:
                payload=raw_data.decode(charset)
            except Exception as e:
                payload=raw_data.decode('gbk')
        except Exception as e:
            logger.error("解码失败",f"{e}\n保留原始值")
            payload=raw_data

        # 按类型存储内容
        if part.get_content_type() == 'text/plain':
            result['text_body'] = payload
        elif part.get_content_type() == 'text/html':
            result['html_body'] = payload
            
    return result

def parse_header(header):
    """解码邮件头信息"""
    try:
        decoded = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded.append(part.decode(encoding or 'utf-8', errors='replace'))
            else:
                decoded.append(part)
        return ''.join(decoded).strip()
    except Exception as e:
        return f"解码失败: {str(e)}"

def parse_date(date_str):
    """解析邮件日期"""
    try:
        return parsedate_to_datetime(date_str).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return '未知时间'
#正文清洗
def clean_text(text):
    # 移除引用内容
    text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)
    # 合并多余空行
    return re.sub(r'\n{3,}', '\n\n', text).strip()

#​敏感信息过滤
def filter_sensitive(text):
    patterns = [
        r'\b(密码|口令)\s*[:：]\s*\S+',  # 过滤密码
        r'\d{4}-\d{4}-\d{4}-\d{4}(-\d{3})?'  # 过滤信用卡号
    ]
    for pattern in patterns:
        text = re.sub(pattern, '[FILTERED]', text)
    return text

def create_secure_context_new():
    # 创建默认安全上下文
    context = ssl.create_default_context()
    
    # 现代协议配置（推荐）
    context.minimum_version = ssl.TLSVersion.TLSv1_2  # 最低使用TLS1.2
    context.maximum_version = ssl.TLSVersion.MAXIMUM_SUPPORTED  # 允许最新协议
    
    # 优化密码套件
    context.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')
    
    # 强制验证配置
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context
def create_secure_context_old():

    # 推荐的安全配置
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True  # 验证主机名匹配证书
    ssl_context.verify_mode = ssl.CERT_REQUIRED  # 强制证书验证

    # 特别针对QQ邮箱的优化
    ssl_context.set_ciphers('ECDHE+AESGCM:!DSS:!aNULL@STRENGTH')  # 使用高安全性密码套件
    ssl_context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # 禁用旧协议
    # 启用SSL调试日志
    ssl_context.post_handshake_auth = True
    ssl_context.keylog_filename = './ssl-key.log'  # 记录密钥（仅调试用）
    return ssl_context


# 日志配置

class EmailMonitor:
    def __init__(self):
        self.config = {
            "host": "imap.qq.com",
            "port": 993,
            # "user": os.getenv("QQ_MAIL_USER"),
            # "password": os.getenv("QQ_MAIL_AUTHCODE"),
            "user": "960902471@qq.com",
            "password": "txxbbjkizzhabdjg",
            "ssl_context": create_secure_context_old(),
        }
        self.last_checked:datetime = None
        self.logger=logger_helper()
    def fetch_recent_emails(self, within_minutes=30):
        """获取指定时间范围内的新邮件"""
        with self._connect_server() as client:
            client.select_folder('INBOX', readonly=True)
            
            # 生成时间筛选条件
            since_time = self._calculate_since_time(within_minutes)
            criteria = self._build_search_criteria(since_time)
            
            # 执行搜索
            messages = client.search(criteria)
            if not messages:
                return []
            
            
            # 批量获取邮件头
            emails = []
            for msg_id, data in client.fetch(messages, ['RFC822.HEADER']).items():
                header = data[b'RFC822.HEADER'].decode()
                email_info = parse_header(header)
                emails.append(email_info)
                # 记录最新邮件时间
                current_time = self._parse_date(email_info['date']).timestamp()
                self.last_checked = max(self.last_checked or 0, current_time)
            
            return emails

    def _calculate_since_time(self, within_minutes):
        """计算起始时间"""
        if self.last_checked:
            # 基于上次检查时间
            return datetime.fromtimestamp(self.last_checked)
        else:
            # 首次检查，获取最近N分钟的邮件
            return datetime.now() - timedelta(minutes=within_minutes)
    
    def _build_search_criteria(self, since_time):
        """构建IMAP搜索条件"""
        # 转换为IMAP日期格式 (DD-Mon-YYYY)
        imap_date = since_time.strftime('%d-%b-%Y')
        return ['OR',
                ['SENTSINCE', imap_date],  # 发件时间筛选
                ['SINCE', imap_date]]      # 收件时间筛选
    
    def _parse_date(self, date_str):
        """精确解析邮件时间"""
        try:
            return parsedate_to_datetime(date_str).astimezone()
        except Exception:
            return datetime.now()
    def _connect_server(self):
        """安全连接IMAP服务器"""
        try:
            client = IMAPClient(
                host=self.config["host"],
                port=self.config["port"],
                ssl_context=self.config["ssl_context"]
            )
            client.login(self.config["user"], self.config["password"])
            return client
        except Exception as e:
            self.logger.error(f"连接失败: {str(e)}")
            return None

    def fecth_emails(self):
            
        new_emails = self.fetch_recent_emails(30)
        for email in new_emails:
            self.logger.info(f"新邮件：{email['subject']} ({email['date']})")
    #标记已读
    def set_email_seen(self, msg_ids:list):
        try:
            with self._connect_server() as client:
                if not client:
                    return
                client.add_flags(msg_ids, [b'\\Seen'], use_uid=True)
        except:
            pass
    
    def check_emails(self):
        """检查新邮件并处理"""
        start_time = time.time()-300
        self.logger.info("开始检查邮件...")
        
        try:
            with self._connect_server() as client:
                if not client:
                    return

                client.select_folder('INBOX', readonly=True)
                since_time = self.last_checked or start_time  # 首次检查近5分钟邮件
                
                flag=f'SINCE {self._format_time(since_time)}'
                
                messages = client.search(['UNSEEN', flag])
                
                if not messages:
                    self.logger.info("未发现新邮件")
                    return

                self.logger.trace(f"发现 {len(messages)} 封新邮件\n{"\n".join([f"ID: {msg_id}" for msg_id in messages])}\n")
                send_times=[]
                
                for msg_id in messages:
                    info=None
                    try:
                        msg_data = client.fetch(msg_id, ['BODY.PEEK[]'])
                        info=self._process_email(msg_data[msg_id][b'BODY[]'])
                    except Exception as e:
                        self.logger.error(f"处理邮件 {msg_id} 失败: {str(e)}")
                    if not info:
                        continue
                    
                    raw_time=info["时　间"]

                    # send_time= datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                    send_times.append({"id":msg_id,"time":raw_time})
                    
                self.logger.trace("邮件发送时间",f"{"\n".join([str(item)  for item in send_times])}")
                self.last_checked = start_time
        except Exception as e:
            self.logger.error(f"检查流程异常: {str(e)}")

    def _format_time(self,  since_time):
        """将时间戳转换为IMAP日期格式"""
        return time.strftime("%d-%b-%Y", time.localtime(since_time))
    def _process_email(self, raw_email):
        """解析并打印邮件内容"""
        parsed = parse_email(raw_email)
      
        
        email_message = BytesParser().parsebytes(raw_email)
        
        info = {
            '发件人': parsed['from'],
            "收件人": parsed['to'],
            "主　题":parsed['subject'],
            "时　间":parsed['date'],
            "正　文":parsed['text_body'] or html_to_text(parsed['html_body']),
        }
        
        self.logger.info("\n" + "\n".join(
            [f"{k}: {v}" for k, v in info.items()]
        ))
        
        return info

    def _get_text_content(self, msg):
        """提取纯文本内容"""
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
        return "无文本内容"

if __name__ == "__main__":
    monitor = EmailMonitor()

    # 初始化调度器
    scheduler = BlockingScheduler()
    scheduler.add_job(
        # monitor.fecth_emails,
        monitor.check_emails,
        'interval',
        minutes=2,
        max_instances=1,
        misfire_grace_time=60
    )
    logger=logger_helper("邮件监控服务","检测新邮件")
    try:
        logger.info("启动")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("终止")
    except Exception as e:
        logger.error("异常",str(e))