import memcache

from . import HandlerBase


class Handler(HandlerBase):

    def __init__(self, host='127.0.0.1', port=11211):
        self.db = memcache.Client(['%s:%s' % (host, port)], debug=0)

    def set(self, sid, data, ttl=0):
        return self.db.set(sid, data, ttl)

    def get(self, sid):
        return self.db.get(sid)

    def delete(self, sid):
        return self.db.delete(sid)
