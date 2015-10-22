import time

import base64
import hashlib
import hmac
import json
import logging
from bottle import request, response, redirect, abort, DEBUG

__version__ = "0.0.4"
__project__ = "bottle-login"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


logger = logging.getLogger(__name__)

class LoginPlugin(object):

    name = 'session'
    api = 2

    def __init__(self):
        self.app = None
        self.user_loader = None

    def setup(self, app):
        if DEBUG:
            logger.setLevel(logging.DEBUG)

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper

    def load_user(self, func):
        self.user_loader = func

    def get_user(self):
        session = request.environ.get('beaker.session')
        user_id = session.get('user_id')
        if not user_id:
            return None
        return self.user_loader(user_id)

    @staticmethod
    def login_user(user_id):
        session = request.environ.get('beaker.session')
        session['user_id'] = user_id
        session.save()

    @staticmethod
    def logout_user():
        session = request.environ.get('beaker.session')
        session.pop('user_id', None)
        session.save()

    def login_required(self, url=None):
        def decorator(callback):
            def wrapper(*args, **kwargs):
                if self.get_user():
                    return callback(*args, **kwargs)

                if url:
                    return redirect(url)

                return abort(401, "Access denied.")
            return wrapper

        if callable(url):
            callback = url
            url = None
            return decorator(callback)

        return decorator


# pylama:ignore=W0621,W0231,W0404,E0710
