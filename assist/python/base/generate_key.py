from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode
import os

def pad(data):
    """
    PKCS7 填充
    """
    block_size = 16
    padding_length = block_size - (len(data) % block_size)
    return data + (chr(padding_length) * padding_length).encode()

def unpad(data):
    """
    PKCS7 去填充
    """
    padding_length = data[-1]
    return data[:-padding_length]

def encrypt_aes_128(key, iv, data):
    """
    使用 AES-128 进行加密

    :param key: 16 字节的密钥
    :param iv: 16 字节的初始化向量
    :param data: 要加密的数据
    :return: 加密后的数据（Base64 编码）
    """
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padded_data = pad(data.encode())
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return b64encode(encrypted_data).decode()

def decrypt_aes_128(key, iv, encrypted_data):
    """
    使用 AES-128 进行解密

    :param key: 16 字节的密钥
    :param iv: 16 字节的初始化向量
    :param encrypted_data: Base64 编码的加密数据
    :return: 解密后的数据
    """
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    encrypted_data = b64decode(encrypted_data)
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return unpad(decrypted_data).decode()

if __name__ == "__main__":

    # 示例用法
    key = os.urandom(16)  # 生成 16 字节的随机密钥
    iv = os.urandom(16)   # 生成 16 字节的随机初始化向量
    data = "Hello,Kitty"

    # 加密
    encrypted_data = encrypt_aes_128(key, iv, data)
    print(f"Encrypted Data: {encrypted_data}")

    # 解密
    decrypted_data = decrypt_aes_128(key, iv, encrypted_data)
    print(f"Decrypted Data: {decrypted_data}")