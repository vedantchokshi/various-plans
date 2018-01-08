"""
All exceptions used by API and database
"""


class BaseApiException(Exception):
    """
    Base exception class for all API exceptions
    """
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
        """
        Used to create a dictionary for jsonifying

        :return: dictionary representation of Exception object
        """
        result = dict()
        result['message'] = self.message
        result['status_code'] = self.status_code
        if self.content is not None:
            for key, value in self.content.items():
                result[key] = value
        return result


class InvalidRequest(BaseApiException):
    """
    Request did not make sense
    """
    status_code = 400


class Unauthorized(BaseApiException):
    """
    User is unauthorized to make the request
    """
    status_code = 401


class ResourceNotFound(BaseApiException):
    """
    Resource requests was not found
    """
    status_code = 404


class InvalidContent(BaseApiException):
    """
    Request content did not make sense
    """
    status_code = 422
