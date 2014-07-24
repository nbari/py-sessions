"""sessions

wsgi middleware for handling sessions
"""

import pickle
import time
import uuid

from Cookie import SimpleCookie
from datetime import datetime, timedelta
from sessions.backends import HandlerBase
from threading import local

"""
thread-local data
"""
data = local()


class Session(object):

    def __init__(self, environ, backend, lifetime):
        self.handler = backend
        self.lifetime = lifetime
        self.sid = None
        self.data = {}
        self.data_hash = None

        if 'HTTP_COOKIE' in environ:
            cookie = SimpleCookie(self.environ['HTTP_COOKIE'])

            if cookie.get('sid'):
                cookie_sid = cookie['sid'].value

                if cookie_sid[:10] != 0 and time.time() < cookie_sid[:10]:
                    self.sid = cookie_sid[10:]

    def read(self, sid):
        pass

    def write(self, sid, session_data):
        pass

    def destroy(self, sid):
        pass

    def start(self):
        if self.sid:
            self.read(self.sid)
        else:
            self.sid = self.make_sid()

        """
        hash for current session data
        """
        self.data_hash = hash(frozenset(self.data.items()))

    def make_sid(self):
        """
        create new sid
        """
        expire = datetime.utcnow() + timedelta(seconds=self.lifetime)
        expire = int(time.mktime((expire).timetuple()))
        return ('%010d' % expire) + uuid.uuid4().hex

    def regenerate_id(self):
        pass

    def save(self):
        # no session is active
        if not self.sid:
            return

        # nothing has changed
        if self.data_hash == hash(frozenset(self.data.items())):
            return

        session_data = pickle.dumps(self.data, 2)

        self.write(self.sid, session_data)

class SessionMiddleware(object):

    """WSGI middleware that adds session support.

    :backend: An instance of the HandlerBase, you can use redis, memcache
    gae_datastore, etc, it just needs to extends the HandlerBas

    :lifetime: ``datetime.timedelta`` that specifies how long a session
    may last. Defaults to 12 hours.
    """

    def __init__(self, app, backend, lifetime=43200):
        self.app = app
        self.backend = backend
        self.lifetime = lifetime

        if not isinstance(backend, HandlerBase):
            raise ValueError('backend must be an instance of HandlerBase')

    def __call__(self, environ, start_response):
        # initialize a session for the current user
        data.session = Session(
            environ=environ,
            backend=self.backend,
            lifetime=self.lifetime)

        """
        PEP-0333 start_response()
        wrapper to insert a cookie into the response headers
        """
        def session_response(status, headers, exc_info=None):
            data.session.save()
            for ch in data.session.make_cookie_headers():
                headers.append(('Set-Cookie', ch))
            return start_response(status, headers, exc_info)

        """
        call the app
        """
        return self.app(environ, session_response)
