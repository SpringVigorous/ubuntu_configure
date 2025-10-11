import abc


class codec_base(metaclass=abc.ABCMeta):
    pass

    @abc.abstractmethod
    def decode(self,data):
        pass
    @abc.abstractmethod
    def encode(self,data):
        pass
    
from base.encode_tools import base64_utf8_to_bytes, bytes_to_base64_utf8,bytes_to_hexex,hexex_to_bytes
class codec_base64(codec_base):
    def decode(self,data):
        return base64_utf8_to_bytes(data)
    def encode(self,data):
        return bytes_to_base64_utf8(data)
    
class codec_hex(codec_base):
    def decode(self,data):
        return hexex_to_bytes(data)
    def encode(self,data):
        return bytes_to_hexex(data)
    
    
from base.generate_key import AES_128
class codec_aes(codec_base):

    def __init__(self,key,iv) -> None:
        self.impl = AES_128(key,  iv)
    def decode(self,data):
        return self.impl.encryept(data)
    def encode(self,data):
        return self.impl.decrypt(data)