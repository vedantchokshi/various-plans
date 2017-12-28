from flask import jsonify, make_response


class ApiException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    @property
    def serialise(self):
        rv = dict()
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


def init(app):
    import api, db
    db.init(app)
    api.init(app)

    @app.errorhandler(ApiException)
    @jsonify
    def api_exception_handler(error):
        return make_response(jsonify(error.serialise), error.status_code)
