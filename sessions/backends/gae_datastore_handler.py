from . import HandlerBase
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from uuid import uuid4


class pySessions(ndb.Model):
    # sid is the key/id
    data = ndb.BlobProperty(required=True)
    expiry = ndb.DateTimeProperty(required=True)

    @classmethod
    def get_sid(cls, sid):
        sid_key = ndb.Key(cls, sid)
        q = pySessions.query(
            pySessions.key == sid_key,
            pySessions.expiry >= datetime.utcnow())
        return q.get()

    @classmethod
    def del_sid(cls, sid):
        sid_key = ndb.Key(cls, sid)
        return sid_key.delete()


class Handler(HandlerBase):

    def set(self, sid, data, ttl=0):
        expire = datetime.utcnow() + timedelta(seconds=ttl)
        try:
            return pySessions(
                id='%s' % sid,
                data=data,
                expiry=expire).put().id()
        except Exception:
            return

    def get(self, sid):
        session = pySessions.get_sid(sid)
        if session:
            return session.data

    def delete(self, sid):
        return pySessions.del_sid(sid)

    def make_sid(self):
        return uuid4().hex
