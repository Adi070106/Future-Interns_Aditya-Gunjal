from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

def get_key_from_password(password, salt):
    return PBKDF2(password, salt, dkLen=16)

def encrypt_file(data, password):
    salt = get_random_bytes(16)
    key = get_key_from_password(password.encode(), salt)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return salt + cipher.nonce + tag + ciphertext

def decrypt_file(data, password):
    salt = data[:16]
    nonce = data[16:32]
    tag = data[32:48]
    ciphertext = data[48:]

    key = get_key_from_password(password.encode(), salt)
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
