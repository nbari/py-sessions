"""sessions

wsgi middleware for handling sessions
"""

import logging
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


def session_start():
    data.session.start()
    return data.session


class Session(object):

    def __init__(self, environ, backend, ttl, cookie_name, log):
        self.handler = backend
        self.ttl = ttl
        self.cookie_name = cookie_name
        self.sid = None
        self.data = {}
        self.data_hash = None
        self.log = log

        if 'HTTP_COOKIE' in environ:
            cookie = SimpleCookie(environ['HTTP_COOKIE'])

            if cookie.get(self.cookie_name):
                cookie_sid = cookie[self.cookie_name].value

                if cookie_sid:
                    self.sid = cookie_sid

    def start(self):
        if self.sid:
            # check if cookie hasn't expired
            if not self.read(self.sid):
                self.sid = uuid.uuid4().hex
        else:
            self.sid = uuid.uuid4().hex

        """
         hash for current session data
        """
        self.data_hash = hash(frozenset(self.data.items()))

    def read(self, sid):
        session_data = self.handler.get(sid)
        if session_data:
            self.data = pickle.loads(session_data)

        else:
            self.data = {}

    def write(self, sid, session_data, ttl):
        pass

    def destroy(self, sid):
        pass

    def make_sid(self):
        expire = datetime.utcnow() + timedelta(seconds=self.ttl)
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

        try:
            self.write(self.sid, session_data, self.ttl)
        except Exception as e:
            self.log.critical('Could not write session: %s' % e)
            return

        return self.sid


class SessionMiddleware(object):

    """WSGI middleware that adds session support.

    :backend: An instance of the HandlerBase, you can use redis, memcache
    gae_datastore, etc, it just needs to extends the HandlerBas

    :ttl: ``datetime.timedelta`` that specifies how long a session
    may last. Defaults to 12 hours.
    """

    def __init__(self, app, backend, ttl=43200, cookie_name='PHPSESSID'):
        self.app = app
        self.backend = backend
        self.ttl = ttl
        self.cookie_name = cookie_name
        self.log = logging.getLogger()

        if not self.log.handlers:
            self.log.addHandler(logging.StreamHandler())

        if not isinstance(backend, HandlerBase):
            raise ValueError('backend must be an instance of HandlerBase')

    def __call__(self, environ, start_response):
        # initialize a session for the current user
        data.session = Session(
            environ=environ,
            backend=self.backend,
            ttl=self.ttl,
            cookie_name=self.cookie_name,
            log=self.log)

        """
        PEP-0333 start_response()
        wrapper to insert a cookie into the response headers
        """
        def session_response(status, headers, exc_info=None):
            sid = data.session.save()
            if sid:
                cookie = SimpleCookie()
                cookie[self.cookie_name] = sid
                cookie[self.cookie_name]['path'] = '/'
                cookie[self.cookie_name]['expires'] = self.ttl

                self.log.debug('Cookie: %s' % cookie.values[0].OutputString())

                headers.append(('Set-Cookie', morsel.OutputString())
                               for morsel in cookie.values())
            return start_response(status, headers, exc_info)

        """
        call the app
        """
        return self.app(environ, session_response)
