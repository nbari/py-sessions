import hashlib
import hmac
import uuid

from . import HandlerBase
from base64 import b64decode, b64encode


class Handler(HandlerBase):

    def __init__(self, cookie_key=None):
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
