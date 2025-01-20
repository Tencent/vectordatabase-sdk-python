from enum import IntEnum


class ErrorCode(IntEnum):
    SUCCESS = 0
    UNEXPECTED_ERROR = -1


class VectorDBException(Exception):
    def __init__(self, code: int = ErrorCode.UNEXPECTED_ERROR, message: str = "") -> None:
        super().__init__()
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    def __str__(self) -> str:
        return f"<{type(self).__name__}: (code={self.code}, message={self.message})>"


class ParamError(VectorDBException):
    """Raise when params are incorrect"""


class NoConnectError(VectorDBException):
    """Connect server fail"""


class ConnectError(VectorDBException):
    """Connect server fail"""


class ServerInternalError(VectorDBException):
    """database core error"""


class DescribeCollectionException(VectorDBException):
    """Raise when describe collection error"""


class GrpcException(VectorDBException):
    """Raise when grpc exception"""
    def __init__(self, code: int = ErrorCode.UNEXPECTED_ERROR, message: str = "") -> None:
        if 'StatusCode.UNAVAILABLE' in message:
            message = f'{message}\n{ERROR_MESSAGE_NETWORK_OR_AUTH}'
        super().__init__(code=code, message=message)


ERROR_MESSAGE_NETWORK_OR_AUTH = '''
Possible Reasons:
1. Incorrect url. Example: http://10.x.x.x
2. Incorrect API key. Example: Tc73SW**********************************
3. Incorrect username. Example: root
4. Network unreachable.
'''
