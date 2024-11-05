from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad ,pad


def encrypt_aes_128(key, iv, data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 加密数据
    padded_data = pad(data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    # 解密数据
    return encrypted_data

def decrypt_aes_128(key, iv, encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 解密数据
    data= unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return data


