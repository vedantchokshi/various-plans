from functools import wraps

from flask import jsonify, make_response


def init(app):
    import plans, events, routes
    app.register_blueprint(plans.ROUTES, url_prefix='/api/plan')
    app.register_blueprint(events.ROUTES, url_prefix='/api/event')
    app.register_blueprint(routes.ROUTES, url_prefix='/api/route')


def jsonify_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        json = kwargs.pop('json', True)
        obj, status_code = func(*args, **kwargs)
        if json:
            if isinstance(obj, list):
                return make_response(jsonify(results=[i.serialise for i in obj]), status_code)
            return make_response(jsonify(obj.serialise), status_code)
        return obj

    return wrapper
