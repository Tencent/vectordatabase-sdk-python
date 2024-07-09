from typing import Optional
from urllib.parse import urlparse

import grpc
from tcvectordb import debug
from tcvectordb.exceptions import ServerInternalError, GrpcException
from tcvectordb.rpc.proto import olama_pb2_grpc, olama_pb2
# from google.protobuf import json_format


class RPCClient:
    def __init__(self,
                 url: str,
                 username: str,
                 key: str,
                 timeout: float = 10,
                 channel_ready_check: bool = True,
                 ):
        options = [
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
        ]
        self.channel = grpc.insecure_channel(self._address(url), options=options)
        self.stub = olama_pb2_grpc.SearchEngineStub(self.channel)
        authorization = 'Bearer account={0}&api_key={1}'.format(username, key)
        self.headers = [('authorization', authorization)]
        self.timeout = timeout

    def close(self):
        self.channel.close()

    def _address(self, url: str):
        _url = urlparse(url)
        if _url.port is None:
            url = '{}:80'.format(url)
        return url.replace('http://', '').replace('https://', '')

    def upsert(self, req: olama_pb2.UpsertRequest, timeout: Optional[float] = None) -> olama_pb2.UpsertResponse:
        # print(json_format.MessageToDict(req))
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UpsertResponse = self.stub.upsert(req, metadata=self.headers, timeout=timeout)
            self._result_check(ret.code, ret.msg, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def search(self, req: olama_pb2.SearchRequest, timeout: Optional[float] = None) -> olama_pb2.SearchResponse:
        # print(json_format.MessageToDict(req))
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.SearchResponse = self.stub.search(req, metadata=self.headers, timeout=timeout)
            self._result_check(ret.code, ret.msg, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def query(self, req: olama_pb2.QueryRequest, timeout: Optional[float] = None) -> olama_pb2.QueryResponse:
        # print(json_format.MessageToDict(req))
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.QueryResponse = self.stub.query(req, metadata=self.headers, timeout=timeout)
            self._result_check(ret.code, ret.msg)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def delete(self, req: olama_pb2.DeleteRequest, timeout: Optional[float] = None) -> olama_pb2.DeleteResponse:
        # print(json_format.MessageToDict(req))
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DeleteResponse = self.stub.dele(req, metadata=self.headers, timeout=timeout)
            self._result_check(ret.code, ret.msg)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def update(self, req: olama_pb2.UpdateRequest, timeout: Optional[float] = None) -> olama_pb2.UpdateResponse:
        # print(json_format.MessageToDict(req))
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UpdateResponse = self.stub.update(req, metadata=self.headers, timeout=timeout)
            self._result_check(ret.code, ret.msg, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def list_databases(self, req: olama_pb2.DatabaseRequest,
                       timeout: Optional[float] = None) -> olama_pb2.DatabaseResponse:
        if timeout is None:
            timeout = self.timeout
        try:
            return self.stub.listDatabases(req, metadata=self.headers, timeout=timeout)
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def _result_check(self, code: int, msg: str, warning: str = None):
        if warning:
            debug.Warning(warning)
        if code != 0:
            raise ServerInternalError(code=code, message=msg)
