"""sessions

wsgi middleware for handling sessions
"""

import hashlib
import hmac
import pickle
import time

from threading import local
from Cookie import CookieError, SimpleCookie
from base64 import b64decode, b64encode
from datetime import datetime
from sessions import backends

"""
thread-local data
"""
data = local()


class Session(object):
    pass


class SessionMiddleware(object):

    def __init__(self, app, cookie_key, backend, lifetime=43200):
        self.app = app
        self.cookie_key = cookie_key
        self.backend = backend
        self.lifetime = lifetime
        if not self.cookie_key:
            raise ValueError("cookie_key MUST be specified")
        if len(self.cookie_key) < 32:
            raise ValueError(
                "RFC2104 recommends you use at least a 32 character key."
                "Try os.urandom(64) to make a key.")

        if not isinstance(backend, backends.SessionHandler):
            pass

    def __call__(self, environ, start_response):
        data.session = Session()

        """PEP-0333 start_response()
        http://legacy.python.org/dev/peps/pep-0333/#the-start-response-callable
        """
        def session_response(status, headers, exc_info=None):
            data.session.save()

        return self.app(environ, session_response)
