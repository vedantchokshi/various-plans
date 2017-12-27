from flask import jsonify

def init(app):
    import plans, events, routes
    app.register_blueprint(plans.ROUTES, url_prefix='/api/plan')
    app.register_blueprint(events.ROUTES, url_prefix='/api/event')
    app.register_blueprint(routes.ROUTES, url_prefix='/api/route')


def jsonify_decorator(func):
    def wrapper(*args, **kwargs):
        json = kwargs.pop('json', True)
        obj = func(*args, **kwargs)
        if json:
            return jsonify(obj.serialise)  # TODO serialise property
        return obj

    return wrapper