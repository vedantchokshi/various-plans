class BaseApiException(Exception):
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


class InvalidRequest(BaseApiException):
    status_code = 400


class Unauthorized(BaseApiException):
    status_code = 401


class ResourceNotFound(BaseApiException):
    status_code = 404


class InvalidInput(BaseApiException):
    status_code = 405
