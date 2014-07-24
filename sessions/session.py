"""sessions

wsgi middleware for handling sessions
"""
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

        if 'HTTP_COOKIE' in environ:
            cookie = SimpleCookie(self.environ['HTTP_COOKIE'])

            if cookie.get('sid'):
                cookie_sid = cookie['sid'].value

                if cookie_sid[:10] != 0 and time.time() < cookie_sid[:10]:
                    self.sid = cookie_sid[10:]

    def read(self, session_id):
        pass

    def write(self, session_id, session_data):
        pass

    def start(self):
        pass

    def make_sid(self):
        expire_dt = datetime.utcnow() + timedelta(seconds=self.lifetime)
        expire_ts = int(time.mktime((expire_dt).timetuple()))
        return ('%010d' % expire_ts) + uuid.uuid4().hex


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
