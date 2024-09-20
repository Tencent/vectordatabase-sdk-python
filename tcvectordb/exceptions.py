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


class IndexTypeException(VectorDBException):
    """Raise when one field is invalid"""


class DescribeCollectionException(VectorDBException):
    """Raise when describe collection error"""


class AIUnsupportedException(VectorDBException):
    """Raise when method unsupported"""

class GrpcException(VectorDBException):
    """Raise when grpc exception"""
