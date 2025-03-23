from libs.py_eth_async.exceptions import *


class BungeeException(Exception):
    pass


class UnsupportedNetwork(BungeeException):
    pass


class NoRoutes(BungeeException):
    pass


class UnacceptableAmount(BungeeException):
    pass


class APIException(BungeeException):
    """
    An exception that occurs when the API is accessed unsuccessfully.

    Attributes:
        response (Optional[dict]): a JSON response to a request.
        status_code (Optional[int]): an HTTP status code.
        message (str): a Bungee error message.

    Args:
        response (Optional[dict]): a JSON response to a request. (None)
        status_code (Optional[int]): an HTTP status code. (None)

    """
    response: Optional[dict]
    status_code: Optional[int]
    message: Optional[str]

    def __init__(self, response: Optional[dict] = None, status_code: Optional[int] = None) -> None:
        self.response = response
        self.status_code = status_code
        self.message = None
        if self.response and isinstance(self.response, dict):
            self.message = self.response.get('message')
            if 'error' in self.response:
                self.message = self.response['error']['message']

    def __str__(self):
        if self.message:
            return f'{self.status_code}: {self.message}'

        return f'{self.status_code} (HTTP)'
