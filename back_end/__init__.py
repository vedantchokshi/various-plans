from flask_sqlalchemy import SQLAlchemy
from flask import jsonify


def register_api_blueprints(app):
    app.register_blueprint(plans.ROUTES, url_prefix='/api/plans')
    app.register_blueprint(events.ROUTES, url_prefix='/api/events')
    app.register_blueprint(routes.ROUTES, url_prefix='/api/routes')


def jsonify_decorator(func):
    def wrapper(*args, **kwargs):
        json = kwargs.pop('json', True)
        obj = func(*args, **kwargs)
        if json:
            return jsonify(obj.serialise)  # TODO serialise property
        return obj

    return wrapper


def init(app):
    global db
    db = SQLAlchemy(app)
    import plans, events, routes, route_events
    db.create_all()


def reset():
    db.drop_all()


# if __name__ == '__main__':
#     # Fake jsonify for testing
#     def jsonify(s):
#         return 'JSON:' + s
#
#
#     @jsonify_decorator
#     def test_func(s):
#         return s + ", test!"
#
#
#     print test_func('lol')
#     print test_func('lol2', json=False)
