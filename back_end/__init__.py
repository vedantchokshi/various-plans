from flask import jsonify, make_response

from back_end.api.api_exceptions import BaseApiException


def init(app):
    import api, db
    db.init(app)
    api.init(app)

    # Because all api errors build off a base exception class,
    # we can catch and deal with them in the same way
    @app.errorhandler(BaseApiException)
    def api_exception_handler(error):
        return make_response(jsonify(error.serialise), error.status_code)
