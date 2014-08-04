from . import HandlerBase
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from uuid import uuid4


class pySessions(ndb.Model):
    # sid is the key/id
    data = ndb.BlobProperty(required=True)
    expiry = ndb.DateTimeProperty(required=True)


class Handler(HandlerBase):

    def set(self, sid, data, ttl=0):
        expire = datetime.utcnow() + timedelta(seconds=ttl)
        try:
            return pySessions(
                id='%s' % sid,
                data=data,
                expiry=expire).put().id()
        except Exception:
            return None

    def get(self, sid):
        session = pySessions.get_by_id(sid)
        if session and session.expiry >= datetime.utcnow():
            return session.data
        return {}

    def delete(self, sid):
        return ndb.Key(pySessions, sid).delete()

    def make_sid(self):
        return uuid4().hex
