class BaseApiException(Exception):
    status_code = 500
    content = {}

    def __init__(self, message, status_code=None, content=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if content is not None:
            self.content = content

    @property
    def serialise(self):
        rv = dict()
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        if self.content is not None:
            for key, value in self.content.items():
                rv[key] = value
        return rv


class InvalidRequest(BaseApiException):
    status_code = 400


class Unauthorized(BaseApiException):
    status_code = 401


class ResourceNotFound(BaseApiException):
    status_code = 404


class InvalidContent(BaseApiException):
    status_code = 422
