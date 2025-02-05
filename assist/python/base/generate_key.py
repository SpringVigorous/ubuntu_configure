from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad ,pad


def encrypt_aes_128(cipher:AES, data):
    if not cipher:
        return data

    # 加密数据
    padded_data = pad(data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    # 解密数据
    return encrypted_data

def decrypt_aes_128(cipher:AES,  encrypted_data):
    if not cipher:
        return encrypted_data

    bytes_data = cipher.decrypt(encrypted_data)
    # 解密数据
    data= unpad(bytes_data, AES.block_size)
    return data

def new_cipher(key,iv):
    return AES.new(key, AES.MODE_CBC, iv)

class AES_128:
    def __init__(self,key,iv) -> None:
        self.cipher = new_cipher(key,  iv) if key and iv else None

    def encryept(self,data):
        return encrypt_aes_128(self.cipher , data)
    
    def decrypt(self,data):
        return decrypt_aes_128(self.cipher , data) 


def encrypt_aes_128_from_key(key, iv, data):
    cipher = new_cipher(key,  iv)

    return encrypt_aes_128(cipher,data)

def decrypt_aes_128_from_key(key, iv, encrypted_data):
    cipher = new_cipher(key,  iv)

    return decrypt_aes_128(cipher,encrypted_data)

if __name__ == '__main__':

    file_path=r"D:\Project\教程\Python全栈0基础入门\2025_01_26 14_39_12.ts" 
    with open(file_path,"rb") as f:
       data= f.read()

    iv=b'\x82q\xba\xe8_d\x87\x00\xce\xd6T}\xb6\xd5o\x08'
    key=b"\xd2f\x85H\xef\n\x85\xf6\x91<m\xf0\xfa'\x92\xa6"

    encrypted_data=encrypt_aes_128_from_key(key, iv, data)
    with open("temp.ts","wb") as f:
        f.write(encrypted_data)
