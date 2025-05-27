import json
import base64

class M3U8Data:
    def __init__(self, url:str,m3u8_url:str,m3u8_data:bytes=None,title:str="默认"):
        """
        初始化M3U8数据对象
        
        :param wp: 包含url和title属性的对象
        :param packet: 包含url和response.body属性的对象
        """
        self.url = url
        self.m3u8_url = m3u8_url
        self.m3u8_data = m3u8_data
        self.title = title

    def to_dict(self, encode_m3u8=False):
        """
        转换为可序列化的字典
        
        :param encode_m3u8: 是否对m3u8_data进行base64编码
        :return: 字典格式数据
        """
        data = {
            "url": self.url,
            "m3u8_url": self.m3u8_url,
            "title": self.title
        }
        
        # 处理二进制数据
        if encode_m3u8:
            data["m3u8_data"] = base64.b64encode(self.m3u8_data).decode('utf-8-sig')
        else:
            try:
                data["m3u8_data"] = self.m3u8_data.decode('utf-8-sig')
            except UnicodeDecodeError:
                raise ValueError("m3u8_data无法转换为UTF-8字符串，请使用base64编码")
        
        return data

class M3U8Encoder(json.JSONEncoder):
    """自定义JSON编码器（自动base64编码二进制数据）"""
    def default(self, obj):
        if isinstance(obj, M3U8Data):
            return obj.to_dict(encode_m3u8=True)
        return super().default(obj)

# 使用示例
if __name__ == "__main__":
    # 假设有以下对象
 
    url = "https://website.com"
    title = "示例标题"
    m3u8_url="https://website.com/m3u8.m3u8"
    m3u8_data="m3u8数据"

    # 创建数据对象
    m3u8_obj = M3U8Data(url,m3u8_url, m3u8_data, title=title)
    
    # 方法1：直接序列化字典
    print(json.dumps(m3u8_obj.to_dict(encode_m3u8=True)))
    
    # 方法2：使用自定义编码器
    print(json.dumps(m3u8_obj, cls=M3U8Encoder))