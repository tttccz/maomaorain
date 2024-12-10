# -*- coding:utf-8 -*-
"""
加密工具類
"""
import base64
import hashlib
import hmac

from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA


def base64Encode(str):
    strByte = str.encode('utf-8')
    return base64.b64encode(strByte).decode('utf-8')


def base64Decode(str):
    strByte = str.encode('utf-8')
    return base64.b64decode(strByte).decode('utf-8')


def md5Encrypt(str):
    import hashlib
    md5 = hashlib.md5()
    md5.update(str.encode('utf-8'))
    return md5.hexdigest()


def sha256_hash(message):
    """
    生成 SHA-256 哈希值
    :param message: 输入消息，字符串类型
    :return: SHA-256 哈希值，字节类型
    """
    sha256 = hashlib.sha256()
    sha256.update(message.encode('utf-8'))
    return sha256.hexdigest()  # 返回字节类型的哈希值


def hex_sha1(input_string):
    # 创建 SHA-1 哈希对象
    sha1 = hashlib.sha1()

    # 更新哈希对象与输入字符串
    sha1.update(input_string.encode('utf-8'))

    # 返回十六进制表示的哈希值
    return sha1.hexdigest()


def hmac_sha256(key, message):
    """
    使用 HMAC-SHA256 生成哈希值
    :param key: 密钥，字节类型
    :param message: 消息，字节类型
    :return: HMAC-SHA256 哈希值，十六进制字符串
    """
    hmac_obj = hmac.new(key, message, hashlib.sha256)
    return hmac_obj.hexdigest()  # 返回十六进制格式的哈希值


def aes_encrypt(salt, iv, data):
    block_size = 16
    # 数据进行 PKCS5Padding 的填充
    pad = lambda s: (s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size))
    data = pad(data)
    # 创建加密对象
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv.encode())
    # 得到加密后的字节码
    encrypted_text = cipher.encrypt(bytes(data, 'utf-8'))
    # base64 编码
    encode_text = base64.b64encode(encrypted_text)
    return encode_text.decode('utf-8')


def aes_decrypt(salt, iv, encrypted):
    # 去掉 PKCS5Padding 的填充
    un_pad = lambda s: s[:-ord(s[len(s) - 1:])]
    # 创建加密对象
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv.encode())
    # base64 解码
    decode_text = base64.b64decode(str(encrypted).encode('utf-8'))
    decrypt_text = un_pad(cipher.decrypt(decode_text)).decode('utf8')
    return decrypt_text


def rsa_encrypt(rsa_publicKey, plaintext):
    rsakey = RSA.importKey(rsa_publicKey)
    cipher = PKCS1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(plaintext.encode('utf-8')))
    return cipher_text.decode('utf-8')


def rsa_decrypt(rsa_privateKey, plaintext):
    # 从字符串导入私钥
    private_key = RSA.importKey(rsa_privateKey)
    # 解码 Base64 密文
    ciphertext = base64.b64decode(plaintext)
    print(ciphertext)
    # 创建解密器
    cipher = PKCS1_v1_5.new(private_key)
    # 解密
    return cipher.decrypt(ciphertext, None).decode('utf-8')
