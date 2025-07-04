from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad ,pad
import os
from pathlib import Path


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

def encrypt_aes_128_from_key(key, iv, data):
    cipher = new_cipher(key,  iv)

    return encrypt_aes_128(cipher,data)

def decrypt_aes_128_from_key(key, iv, encrypted_data):
    cipher = new_cipher(key,  iv)

    return decrypt_aes_128(cipher,encrypted_data)


class AES_128:
    def __init__(self,key,iv) -> None:
        self.cipher = new_cipher(key,  iv) if key and iv else None
    def encryept(self,data):
        return encrypt_aes_128(self.cipher , data) if self.cipher else data
    def decrypt(self,data):
        return decrypt_aes_128(self.cipher , data)  if self.cipher else data

def decrypt_dir_aes_128(key, iv,dir_path):
    if not os.path.exists(dir_path):
        print(f"错误: 指定的目录 '{dir_path}' 不存在")
        return
    aes=AES_128(key, iv)
    
    # 获取所有 .ts 文件
    ts_files = list(Path(dir_path).rglob('*.ts'))
    
    if not ts_files:
        print(f"在目录 '{dir_path}' 及其子目录中未找到 .ts 文件")
        return

    print(f"找到 {len(ts_files)} 个 .ts 文件，开始处理...")
    
    # 处理每个 .ts 文件
    for file_path in ts_files:
        file_path = str(file_path)
        try:
            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = f.read()
            if content:
                with open(file_path, 'wb') as f:
                    f.write(aes.decrypt(content))

            print(f"成功处理: {file_path}")
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")

if __name__ == '__main__':

    key=b'G5gn3dZxP5ErztBB'
    iv=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    decrypt_dir_aes_128(key, iv,r"F:\worm_practice\player\temp-1\67f6ba6e")
    
    exit(0)

    file_path=r"F:\worm_practice\player\temp-1\67f6ba6e\0067.ts" 
    with open(file_path,"rb") as f:
       data= f.read()
    print(bool(iv))

    
    org_path=Path(file_path)
    dest_path=org_path.with_stem(org_path.stem+"_decrypted")
    
    
    
    # encrypted_data=decrypt_aes_128_from_key(key, iv, data)
    aes=AES_128(key, iv)
    encrypted_data=aes.decrypt(data)
    
    with open(str(dest_path),"wb") as f:
        f.write(encrypted_data)
