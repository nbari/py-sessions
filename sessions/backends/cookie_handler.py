import hashlib

from . import HandlerBase
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64decode, b64encode


class Handler(HandlerBase):

    def __init__(self, cookie_key=None):
        self.data = None
        self.cookie_key = cookie_key
        if not self.cookie_key:
            raise ValueError('cookie_key MUST be specified')
        if len(self.cookie_key) < 32:
            raise ValueError('Use at least a 32 character key.')

    def set(self, sid, data, ttl=0):
        return sid

    def get(self, sid):
        return self.db.get(sid)

    def delete(self, sid):
        return self.db.delete(sid)

    def make_sid(self):
        return '--cookie--'


class Crypt(object):

    def derive_key_and_iv(self, password, salt, key_length, iv_length):
        d = d_i = ''
        while len(d) < key_length + iv_length:
            d_i = hashlib.md5(d_i + password + salt).digest()
            d += d_i
        return d[:key_length], d[key_length:key_length + iv_length]

    def encrypt(self, data, password, key_length=32):
        def pad(s):
            x = AES.block_size - len(s) % AES.block_size
            return s + (chr(x) * x)

        data = pad(data)
        """
        AES.block_size 16 - len('Salted__') 8
        """
        salt = Random.new().read(AES.block_size - 8)

        key, iv = self.derive_key_and_iv(
            password, salt, key_length, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        return b64encode('Salted__%s%s' % (salt, cipher.encrypt(data)))

    def decrypt(self, data, password, key_length=32):
        unpad = lambda s: s[:-ord(s[-1])]

        data = b64decode(data)

        salt = data[8:16]
        data = data[16:]

        key, iv = self.derive_key_and_iv(
            password, salt, key_length, AES.block_size)

        cipher = AES.new(key, AES.MODE_CBC, iv)

        return unpad(cipher.decrypt(data))
