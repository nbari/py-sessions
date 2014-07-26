import redis
from . import HandlerBase


class Handler(HandlerBase):

    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.db = redis.StrictRedis(host, port, db)

    def set(self, sid, data, ttl=0):
        return self.db.setex(sid, ttl, data)

    def get(self, sid):
        return self.db.get(sid)

    def delete(self, sid):
        return self.db.delete(sid)
