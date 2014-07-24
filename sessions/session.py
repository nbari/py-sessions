"""sessions

wsgi middleware for handling sessions

see also
https://github.com/dound/gae-sessions/blob/master/gaesessions/__init__.py
"""

import hashlib
import hmac
import pickle
import time

from Cookie import SimpleCookie
from base64 import b64decode, b64encode
from datetime import datetime
from sessions.backends import HandlerBase
from threading import local

"""
thread-local data
"""
data = local()


class Session(object):

    def __init__(self, environ, cookie_key, backend, lifetime):
        self.environ = environ
        self.cookie_key = cookie_key
        self.handler = backend
        self.lifetime = lifetime
        self.sid = None
        self.read_cookie()

    def read_cookie(self):
        if 'HTTP_COOKIE' in self.environ:
            cookie = SimpleCookie(self.environ['HTTP_COOKIE'])

            if cookie.get('sid'):
                self.sid = cookie['sid'].value
            else:
                self.sid = None


class SessionMiddleware(object):

    """WSGI middleware that adds session support.

    :cookie_key: A key used to secure cookies so users cannot modify their
    content.  Keys should be at least 32 bytes (RFC2104).  Tip: generate
    your key using ``os.urandom(32).encode('hex')``

    :backend: An instance of the HandlerBase, you can use redis, memcache
    gae_datastore, etc, it just needs to extends the HandlerBas

    :lifetime: ``datetime.timedelta`` that specifies how long a session
    may last. Defaults to 12 hours.
    """

    def __init__(self, app, cookie_key, backend, lifetime=43200):
        self.app = app
        self.cookie_key = cookie_key
        self.backend = backend
        self.lifetime = lifetime
        if not self.cookie_key:
            raise ValueError('cookie_key MUST be specified')

        if len(self.cookie_key) < 32:
            raise ValueError(
                "RFC2104 recommends you use at least a 32 character key.")

        if not isinstance(backend, HandlerBase):
            raise ValueError('backend must be an instance of HandlerBase')

    def __call__(self, environ, start_response):
        # initialize a session for the current user
        data.session = Session(
            environ=environ,
            cookie_key=self.cookie,
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
