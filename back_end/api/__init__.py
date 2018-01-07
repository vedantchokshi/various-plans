"""
Initialise API function and useful function decorators
"""
import time
from functools import wraps

from flask import jsonify, make_response, request
from google.auth.transport import requests
from google.oauth2 import id_token

from back_end.exceptions import Unauthorized


def init(app, prefix):
    """
    Initialise the app with the blueprints defined in this module

    :param app: Flask application
    :param prefix: URL prefix for all API URLs
    """
    # pylint: disable-msg=cyclic-import
    # Imports are safe as they are called inside this function
    import back_end.api.plans as plans
    import back_end.api.events as events
    import back_end.api.routes as routes
    import back_end.api.users as users
    app.register_blueprint(plans.ROUTES, url_prefix='{}/plan'.format(prefix))
    app.register_blueprint(events.ROUTES, url_prefix='{}/event'.format(prefix))
    app.register_blueprint(routes.ROUTES, url_prefix='{}/route'.format(prefix))
    app.register_blueprint(users.ROUTES, url_prefix='{}/user'.format(prefix))


def get_userid_from_token(token):
    """
    Use Google oauth2 service to verify a Google signin token

    :return: Google Auth user ID
    :rtype: str
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(),
            "952476275187-ef3icj10cn4ptsl3ehs3jcg3tdeff0pv.apps.googleusercontent.com"
        )

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        return idinfo['sub']
    except ValueError:
        raise Unauthorized('Invalid token')


def token_decorator(func):
    """
    Get the Google signin token from the request cookie `vp-token` and
    pass it as the decorated function as the argument `userid` for authorisation.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # pylint: disable-msg=missing-docstring
        # @wraps takes the docstring from the wrapped function
        token = request.cookies.get('vp-token')
        if token is not None:
            userid = get_userid_from_token(token)
            kwargs['userid'] = userid
            return func(*args, **kwargs)
        raise Unauthorized('Please log in')
        #raise Unauthorized('No token in cookies')

    return wrapper


def jsonify_decorator(func):
    """
    Take the result of the decorated function and create a json response.

    Functions must return a tuple of `(object, status_code)`.

    The object may be a list of objects but all objects must implement `.serialise`
    which returns a dictionary representation of themselves.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # pylint: disable-msg=missing-docstring
        # @wraps takes the docstring from the wrapped function
        timestamp = time.time()
        json = kwargs.pop('json', True)
        obj, status_code = func(*args, **kwargs)
        if json:
            if isinstance(obj, list):
                _d = dict()
                _d['results'] = [i.serialise for i in obj]
                obj = _d
            else:
                obj = obj.serialise
            obj['timestamp'] = timestamp
            return make_response(jsonify(obj), status_code)
        return obj

    return wrapper
