import plans, locations, routes


def register_api_blueprints(app):
    app.register_blueprint(plans.ROUTES, url_prefix='/api/plans')
    app.register_blueprint(locations.ROUTES, url_prefix='/api/locations')
    app.register_blueprint(routes.ROUTES, url_prefix='/api/routes')
