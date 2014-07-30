py-sessions
===========

Python middleware for handling sessions


Session storage backends
------------------------

The backend must follow the [HandlerBase](https://github.com/nbari/py-sessions/blob/master/sessions/backends/__init__.py) abstract class.
currenlty the suported backends are:

* GAE_memcache
* GAE_datastore
* memcache
* redis
* cookie (encrypted cookies)


How to use
----------

To work with ``sessions`` you need to set it up as an middleware

Setting up as middleware
------------------------

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

Using encrypted cookies
-----------------------

For using only cookies the cookie_handler is needed:

    from sessions.backends import cookie_handler

A ``cookie_key`` must be specified:

    sessions_backend = cookie_handler.Handler('90875de1cb12c1efab39dc73c8cb053d')



Using sessions
--------------

    import sessions

    session = sessions.session_start()

    if 'test' in session:
        session['test'] += 1
        print session['test']
    else:
        session['test'] = 1

    # To destroy a session
    session.destroy()

    # To get a new session id
    session.regenerate_id()



pip install python-memcached
pip install redis

References:
* https://github.com/dound/gae-sessions
* http://php.net/manual/en/class.sessionhandlerinterface.php
* http://docs.zunzun.io
