from . import plans, events, routes

def register_api_blueprints(app):
    app.register_blueprint(plans.ROUTES, url_prefix='/api/plans')
    app.register_blueprint(events.ROUTES, url_prefix='/api/events')
    app.register_blueprint(routes.ROUTES, url_prefix='/api/routes')
