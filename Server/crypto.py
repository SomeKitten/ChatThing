# a good chunk from https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python

import base64
import random
import time

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding


def write_b64(name, data):
    try:
        file_content = base64.b64decode(data)
        with open(name, "wb+") as f:
            f.write(file_content)
    except Exception as e:
        print(str(e))


def read_b64(name):
    try:
        with open(name, "rb") as f:
            file_content = f.read()
            return base64.b64encode(file_content).decode("utf-8")
    except Exception as e:
        print(str(e))


def try_login(password, username, ip):
    try:
        decrypt(password.encode(), read_b64("cache/{}".format(username))).decode()
        random.seed(time.time())
        key = random.getrandbits(4 * 12)
        key = base64.b64encode(str(key).encode('ascii'))
        print(key)
        write_b64("local_cache/{}".format(ip), key)
        return encrypt(key, "{}\n{}".format(password, username).encode())
    except ValueError:
        return False


def register(password, username):
    write_b64("cache/{}".format(username), encrypt(password.encode(), username.encode()))


def token_login(ip, token):
    return decrypt(read_b64("local_cache/{}".format(ip)).encode(), token)
