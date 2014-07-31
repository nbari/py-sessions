"""sessions

wsgi middleware for handling sessions
"""

import hashlib
import logging
import pickle

from Cookie import SimpleCookie
from sessions.backends import HandlerBase
from threading import local

# thread-local data
data = local()


def session_start():
    data.session.start()
    return data.session


class Session(object):

    def __init__(self, environ, backend, ttl, cookie_name, fp_use_ip, log):
        self.handler = backend
        self.ttl = ttl
        self.cookie_name = cookie_name
        self.sid = None
        self.data = {}
        self.log = log
        self.clear_cookie = False

        fingerprint = '%s%s%s%s' % (environ.get('HTTP_ACCEPT'),
                                    environ.get('HTTP_USER_AGENT'),
                                    environ.get('HTTP_ACCEPT_ENCODING'),
                                    environ.get('HTTP_ACCEPT_LANGUAGE'))
        if fp_use_ip:
            fingerprint += environ.get('REMOTE_ADDR')

        self.fingerprint = hashlib.sha1(fingerprint).hexdigest()

        if 'HTTP_COOKIE' in environ:
            cookie = SimpleCookie(environ['HTTP_COOKIE'])

            if cookie.get(self.cookie_name):
                cookie_sid = cookie[self.cookie_name].value

                if cookie_sid:
                    self.sid = cookie_sid

    def start(self):
        if self.sid:
            # check if cookie exists and hasn't expired
            self.data = self._read(self.sid)
            if not self.data:
                self.sid = self.handler.make_sid()
        else:
            self.sid = self.handler.make_sid()

    def _read(self, sid):
        session_data = self.handler.get(sid)
        if session_data:
            session_data = pickle.loads(session_data)
            # check the fingerprint
            if '_@' in session_data:
                if session_data['_@'] == self.fingerprint:
                    return session_data
        return {}

    def _write(self, sid, session_data):
        return self.handler.set(sid, session_data, self.ttl)

    def destroy(self):
        self.handler.delete(self.sid)
        self.data = {}
        self.clear_cookie = True

    def regenerate_id(self):
        self.handler.delete(self.sid)
        self.sid = self.handler.make_sid()

    def close(self):
        if not self.sid:
            return

        if self.clear_cookie:
            return self.sid

        self.data['_@'] = self.fingerprint

        session_data = pickle.dumps(self.data, 2)

        try:
            return self._write(self.sid, session_data)
        except Exception as e:
            self.log.critical('Could not write session: %s' % e)
            return

    def __getitem__(self, key):
        """Returns the value associated with key on this session."""
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        """Set a value named key on this session."""
        self.data.__setitem__(key, value)

    def __delitem__(self, key):
        """Deletes the value associated with key on this session."""
        self.data.__delitem__(key)

    def __iter__(self):
        """Returns an iterator over the keys (names) of the stored values."""
        return self.data.iterkeys()

    def __contains__(self, key):
        """Returns True if key is present on this session."""
        return self.data.__contains__(key)

    def __str__(self):
        """Returns a string representation of the session."""
        return "SID=%s %s" % (self.sid, self.data)


class SessionMiddleware(object):

    """WSGI middleware that adds session support.

    :app: The framework application to call

    :backend: An instance of the HandlerBase, you can use redis, memcache
    gae_datastore, etc, it just needs to extends the HandlerBas

    :ttl: Specifies how long a session may last. Defaults to 12 hours.

    :cookie_name: Name of the cookie to use.

    :fp_use_ip: True or False, use the client IP or not for the fingerprint,
    defaults to True
    """

    def __init__(self, app, backend, ttl=43200, cookie_name='SID',
                 fp_use_ip=True):
        self.app = app
        self.backend = backend
        self.ttl = ttl
        self.cookie_name = cookie_name
        self.fp_use_ip = fp_use_ip
        self.log = logging.getLogger()

        if not self.log.handlers:
            self.log.addHandler(logging.StreamHandler())

        if not isinstance(backend, HandlerBase):
            raise ValueError('backend must be an instance of HandlerBase')

    def __call__(self, environ, start_response):
        # initialize a session for the current user
        data.session = Session(environ=environ,
                               backend=self.backend,
                               ttl=self.ttl,
                               cookie_name=self.cookie_name,
                               fp_use_ip=self.fp_use_ip,
                               log=self.log)

        """PEP-0333 start_response()
        wrapper to insert a cookie into the response headers
        """
        def session_response(status, headers, exc_info=None):
            sid = data.session.close()
            if sid:
                cookie = SimpleCookie()

                if data.session.clear_cookie:
                    cookie[self.cookie_name] = ''
                    cookie[self.cookie_name]['expires'] = -86400
                else:
                    cookie[self.cookie_name] = sid
                    cookie[self.cookie_name]['expires'] = self.ttl

                cookie[self.cookie_name]['path'] = '/'
                cookie = cookie[self.cookie_name].OutputString()

                self.log.debug('Cookie: %s' % cookie)

                headers.append(('Set-Cookie', cookie))

            return start_response(status, headers, exc_info)
        return self.app(environ, session_response)
