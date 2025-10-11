
import json

import sys
import os




from email_sender import EmailSender,ImageMode


from  com_decorator import exception_decorator
from base.string_tools import exe_dir

@exception_decorator()
def load_setting():
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
        
        return sender_email,password,receiver_email

@exception_decorator()
def send_email_by_config(subject,body:str,body_type='plain',attachment_path:str|list=None,bodyfiles:str|list=None,image_mode:ImageMode=ImageMode.INSERT):
        
        sender_email,password,receiver_email=load_setting() 
        
        
        email_sender = EmailSender(sender_email, password)
        # attachment_list=attachment_path if type(attachment_path)==list else [attachment_path] if attachment_path is not None else []
        # bodyfiles_list=bodyfiles if type(bodyfiles)==list else [bodyfiles] if bodyfiles is not None else []
        
        email_sender.send_email(receiver_email, subject, body,body_type, attachment_path, bodyfiles,image_mode)
@exception_decorator()
def send_email(receiver_email,subject,body:str,body_type='plain',attachment_path:str|list=None,bodyfiles:str|list=None,image_mode:ImageMode=ImageMode.INSERT):
        
        sender_email,password,_=load_setting() 
        
        
        email_sender = EmailSender(sender_email, password)
        # attachment_list=attachment_path if type(attachment_path)==list else [attachment_path] if attachment_path is not None else []
        # bodyfiles_list=bodyfiles if type(bodyfiles)==list else [bodyfiles] if bodyfiles is not None else []
        
        email_sender.send_email(receiver_email, subject, body,body_type, attachment_path, bodyfiles,image_mode)
@exception_decorator()
def send_emails_by_config(subject:str,body_dict:dict,body_type='plain',attachment_path:str|list=None,bodyfiles:str|list=None,image_mode:ImageMode=ImageMode.INSERT):
        
        sender_email,password,receiver_email=load_setting() 
        
        
        email_sender = EmailSender(sender_email, password)
        # attachment_list=attachment_path if type(attachment_path)==list else [attachment_path] if attachment_path is not None else []
        # bodyfiles_list=bodyfiles if type(bodyfiles)==list else [bodyfiles] if bodyfiles is not None else []
        
        body_vals=list(body_dict.values())
        body_names=list(body_dict.keys())
        
        for name,recievers in receiver_email.items():
            dest=[]
            if name not in body_dict:
                dest=body_vals
            else:
                index=body_names.index(name)
                dest.append(body_vals[index])
                others=[body_vals[i] for i in range(len(body_names)) if i!=index]
                dest.extend(others)
            body="\n".join(dest)
        
        # for name,body in body_dict.items():
        #     if name not in receiver_email:
        #         continue
        #     receiver=receiver_email[name]
            
            
            
            email_sender.send_email(recievers, subject, body,body_type, attachment_path, bodyfiles,image_mode=image_mode)
        

    
    
    

if __name__ == '__main__':
    send_email_by_config('test subject','test body',body_type='plain',
               attachment_path=["F:/教程/多肉/哔哩哔哩视频/26 风车草属『1-24』.mp4",
                                "F:/教程/多肉/哔哩哔哩视频/26 风车草属『1-24』.ai-zh.srt",
                                "F:/教程/多肉/哔哩哔哩视频/26 风车草属『1-24』.ass"
])