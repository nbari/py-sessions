import uuid

from . import HandlerBase
from google.appengine.api import memcache


class Handler(HandlerBase):

    def set(self, sid, data, ttl=0):
        if memcache.set(sid, data, ttl):
            return sid

    def get(self, sid):
        return memcache.get(sid)

    def delete(self, sid):
        return memcache.delete(sid)

    def make_sid(self):
        return uuid.uuid4().hex
