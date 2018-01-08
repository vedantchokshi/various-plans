"""
Initialise the database and API
"""
from flask import jsonify, make_response

from back_end.exceptions import BaseApiException


def init(app):
    """
    Initial setup of application.

    Creates an error handler
    """
    import back_end.api
    import back_end.db
    back_end.db.init(app)
    back_end.api.init(app, '/api')

    # Because all api errors build off a base exception class,
    # we can catch and deal with them in the same way
    # pylint: disable-msg=unused-variable
    # function is used by Flask
    @app.errorhandler(BaseApiException)
    def api_exception_handler(error):
        """
        Take an API exception and turn it into a server response
        """
        return make_response(jsonify(error.serialise), error.status_code)
