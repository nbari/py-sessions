py-sessions
===========

Python middleware for handling sessions

Server-side only
----------------

Session data is stored only in server-side not in the client side via cookie.


Session storage backends
------------------------

The backend must follow the (HandlerBase)[https://github.com/nbari/py-sessions/blob/master/sessions/backends/__init__.py] abstract class.
currenlty the suported backends are:

* GAE_memcache
* GAE_datastore
* memcache
* redis



How to use
----------

To work with ``sessions`` you need to set it up as an middleware

Example
.......

    import sessions
    import zunzuncito

    from sessions.backends import redis_handler

    root = 'my_app'
    versions = ['v0', 'v1']

    app = zunzuncito.ZunZun(
        root,
        versions,
        rid='REQUEST_LOG_ID',
        debug=True)

    # Sessions middleware
    sessions_backend = redis_handler.Handler()
    app = sessions.SessionMiddleware(app, sessions_backend)


References:
* https://github.com/dound/gae-sessions
* http://php.net/manual/en/class.sessionhandlerinterface.php
* http://docs.zunzun.io
