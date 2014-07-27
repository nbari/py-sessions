from google.appengine.api import memcache

from . import HandlerBase


class Handler(HandlerBase):

    def set(self, sid, data, ttl=0):
        return memcache.add(sid, data, ttl)

    def get(self, sid):
        return memcache.get(sid)

    def delete(self, sid):
        return memcache.delete(sid)
