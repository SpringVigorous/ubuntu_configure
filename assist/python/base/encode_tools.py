import base64

def bytes_to_base64_utf8(byte_data:bytes):
    # 将 bytes 对象编码为 Base64 字符串
    base64_encoded = base64.b64encode(byte_data)

    # 将 Base64 字节序列解码为 UTF-8 字符串
    base64_string = base64_encoded.decode('utf-8')
    return base64_string

def base64_utf8_to_bytes(base64_string:str):
    # 将 Base64 字符串编码为字节序列
    base64_encoded = base64_string.encode('utf-8')

    # 将 Base64 字节序列解码为 bytes 对象
    byte_data = base64.b64decode(base64_encoded)
    return  byte_data


def bytes_to_hexex(byte_data:bytes):
    hex_string = byte_data.hex()
    return hex_string

def hexex_to_bytes(hex_string:str):
    byte_data = bytes.fromhex(hex_string)
    return byte_data



if __name__ == '__main__':
        # 示例 bytes 对象
    byte_data = b'\x82\x71\xba\xe8\x5f\x64\x87\x00\xce\xd6\x54\x7d\xb6\xd5\x6f\x08'
    base64_string = bytes_to_base64_utf8(byte_data)
    print(base64_string)  # 输出: gnc66OlfRHADztZUfbbVbwg=

    byte_data =base64_utf8_to_bytes(base64_string)
    print(byte_data)





