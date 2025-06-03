import random
from typing import Optional
from urllib.parse import urlparse

import grpc
from tcvectordb import debug
from tcvectordb.exceptions import ServerInternalError, GrpcException
from tcvectordb.rpc.proto import olama_pb2_grpc, olama_pb2
from google.protobuf import json_format


class RPCClient:
    """Grpc client for VectorDB's API"""

    def __init__(self,
                 url: str,
                 username: str,
                 key: str,
                 timeout: float = 10,
                 password: Optional[str] = None,
                 pool_size: int = 1,
                 **kwargs):
        self.url = url
        if password is None:
            password = key
        authorization = 'Bearer account={0}&api_key={1}'.format(username, password)
        self.headers = [('authorization', authorization)]
        self.timeout = timeout
        self.pool_size = pool_size
        self.direct = False
        self.channels = [ self.create_stub(index=i) for i in range(pool_size)]
        self.stubs = [olama_pb2_grpc.SearchEngineStub(channel) for channel in self.channels]

    def create_stub(self, index=0):
        options = [
            ('grpc.max_send_message_length', 100 * 1024 * 1024 + index),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024 + index)
        ]
        return grpc.insecure_channel(self._address(self.url), options=options)

    def get_stub(self) -> olama_pb2_grpc.SearchEngineStub:
        return self.stubs[random.randrange(self.pool_size)]

    def close(self):
        for ch in self.channels:
            ch.close()

    def _get_headers(self, ai: bool):
        headers = []
        backend = "vdb"
        if not self.direct and ai:
            backend = "ai"
            headers.append(('backend-service', 'ai'))
        else:
            headers.append(('backend-service', 'vdb'))
        headers.extend(self.headers)
        # debug.Debug("Backend %s", backend)
        return headers

    def _address(self, url: str):
        _url = urlparse(url)
        if _url.port is None:
            url = '{}:80'.format(url)
        return url.replace('http://', '').replace('https://', '')

    def upsert(self,
               req: olama_pb2.UpsertRequest,
               timeout: Optional[float] = None,
               ai: bool = False) -> olama_pb2.UpsertResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UpsertResponse = self.get_stub().upsert(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def search(self,
               req: olama_pb2.SearchRequest,
               timeout: Optional[float] = None,
               ai: bool = False) -> olama_pb2.SearchResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.SearchResponse = self.get_stub().search(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def hybrid_search(self,
                      req: olama_pb2.SearchRequest,
                      timeout: Optional[float] = None,
                      ai: bool = False) -> olama_pb2.SearchResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.SearchResponse = self.get_stub().hybrid_search(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def fulltext_search(self,
                        req: olama_pb2.SearchRequest,
                        timeout: Optional[float] = None) -> olama_pb2.SearchResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.SearchResponse = self.get_stub().full_text_search(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def query(self,
              req: olama_pb2.QueryRequest,
              timeout: Optional[float] = None,
              ai: bool = False) -> olama_pb2.QueryResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.QueryResponse = self.get_stub().query(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def delete(self,
               req: olama_pb2.DeleteRequest,
               timeout: Optional[float] = None,
               ai: bool = False) -> olama_pb2.DeleteResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DeleteResponse = self.get_stub().dele(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def update(self,
               req: olama_pb2.UpdateRequest,
               timeout: Optional[float] = None,
               ai: bool = False) -> olama_pb2.UpdateResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UpdateResponse = self.get_stub().update(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def explain(self,
                req: olama_pb2.ExplainRequest,
                timeout: Optional[float] = None,
                ) -> olama_pb2.ExplainResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.ExplainResponse = self.get_stub().explain(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def count(self,
              req: olama_pb2.CountRequest,
              timeout: Optional[float] = None,
              ) -> olama_pb2.CountResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.CountResponse = self.get_stub().count(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def create_database(self,
                        req: olama_pb2.DatabaseRequest,
                        timeout: Optional[float] = None,
                        ai: bool = False) -> olama_pb2.DatabaseResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DatabaseResponse = self.get_stub().createDatabase(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def drop_database(self,
                      req: olama_pb2.DatabaseRequest,
                      timeout: Optional[float] = None,
                      ai: bool = False) -> olama_pb2.DatabaseResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DatabaseResponse = self.get_stub().dropDatabase(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def list_databases(self,
                       req: olama_pb2.DatabaseRequest,
                       timeout: Optional[float] = None,
                       ai: bool = False) -> olama_pb2.DatabaseResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DatabaseResponse = self.get_stub().listDatabases(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def set_alias(self,
                  req: olama_pb2.AddAliasRequest,
                  timeout: Optional[float] = None,
                  ai: bool = False) -> olama_pb2.UpdateAliasResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UpdateAliasResponse = self.get_stub().setAlias(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def delete_alias(self,
                     req: olama_pb2.RemoveAliasRequest,
                     timeout: Optional[float] = None,
                     ai: bool = False) -> olama_pb2.UpdateAliasResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UpdateAliasResponse = self.get_stub().deleteAlias(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def rebuild_index(self,
                      req: olama_pb2.RebuildIndexRequest,
                      timeout: Optional[float] = None,
                      ai: bool = False) -> olama_pb2.RebuildIndexResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.RebuildIndexResponse = self.get_stub().rebuildIndex(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def add_index(self,
                  req: olama_pb2.AddIndexRequest,
                  timeout: Optional[float] = None,
                  ai: bool = False) -> olama_pb2.AddIndexResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.AddIndexResponse = self.get_stub().addIndex(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def drop_index(self,
                   req: olama_pb2.DropIndexRequest,
                   timeout: Optional[float] = None,
                   ai: bool = False) -> olama_pb2.DropIndexResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DropIndexResponse = self.get_stub().dropIndex(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def modify_vector_index(self,
                            req: olama_pb2.ModifyVectorIndexRequest,
                            timeout: Optional[float] = None,
                            ai: bool = False) -> olama_pb2.ModifyVectorIndexResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.ModifyVectorIndexResponse = self.get_stub().modifyVectorIndex(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def create_collection(self,
                          req: olama_pb2.CreateCollectionRequest,
                          timeout: Optional[float] = None,
                          ai: bool = False) -> olama_pb2.CreateCollectionResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.CreateCollectionResponse = self.get_stub().createCollection(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def drop_collection(self,
                        req: olama_pb2.DropCollectionRequest,
                        timeout: Optional[float] = None,
                        ai: bool = False) -> olama_pb2.DropCollectionResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DropCollectionResponse = self.get_stub().dropCollection(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def list_collections(self,
                         req: olama_pb2.ListCollectionsRequest,
                         timeout: Optional[float] = None,
                         ai: bool = False) -> olama_pb2.ListCollectionsResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.ListCollectionsResponse = self.get_stub().listCollections(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def describe_collection(self,
                            req: olama_pb2.DescribeCollectionRequest,
                            timeout: Optional[float] = None,
                            ai: bool = False) -> olama_pb2.DescribeCollectionResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.DescribeCollectionResponse = self.get_stub().describeCollection(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def truncate_collection(self,
                            req: olama_pb2.TruncateCollectionRequest,
                            timeout: Optional[float] = None,
                            ai: bool = False) -> olama_pb2.TruncateCollectionResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.TruncateCollectionResponse = self.get_stub().truncateCollection(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def create_user(self,
                    req: olama_pb2.UserAccountRequest,
                    timeout: Optional[float] = None,
                    ) -> olama_pb2.UserAccountResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UserAccountResponse = self.get_stub().user_create(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def grant_permission(self,
                         req: olama_pb2.UserPrivilegesRequest,
                         timeout: Optional[float] = None,
                         ) -> olama_pb2.UserPrivilegesResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UserPrivilegesResponse = self.get_stub().user_grant(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def revoke_permission(self,
                          req: olama_pb2.UserPrivilegesRequest,
                          timeout: Optional[float] = None,
                          ) -> olama_pb2.UserPrivilegesResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UserPrivilegesResponse = self.get_stub().user_revoke(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def describe_user(self,
                      req: olama_pb2.UserDescribeRequest,
                      timeout: Optional[float] = None,
                      ) -> olama_pb2.UserDescribeResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UserDescribeResponse = self.get_stub().user_describe(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def list_users(self,
                   req: olama_pb2.UserListRequest,
                   timeout: Optional[float] = None,
                   ) -> olama_pb2.UserListResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UserListResponse = self.get_stub().user_list(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def drop_user(self,
                  req: olama_pb2.UserAccountRequest,
                  timeout: Optional[float] = None,
                  ) -> olama_pb2.UserAccountResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UserAccountResponse = self.get_stub().user_drop(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def change_password(self,
                        req: olama_pb2.UserAccountRequest,
                        timeout: Optional[float] = None,
                        ) -> olama_pb2.UserAccountResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.UserAccountResponse = self.get_stub().user_change_password(
                req, metadata=self._get_headers(False), timeout=timeout)
            self._result_check(ret)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def _print_req(self, req):
        if debug.DebugEnable:
            debug.Debug('%s body=%s', req.__class__.__name__,
                        json_format.MessageToDict(req, preserving_proto_field_name=True))

    def _result_check(self, ret, warning: str = None):
        code = ret.code
        msg = ret.msg
        if code != 0:
            raise ServerInternalError(code=code, message=msg)
        if warning:
            debug.Warning(warning)
        if debug.DebugEnable:
            debug.Debug('%s response=%s', ret.__class__.__name__,
                        json_format.MessageToDict(ret, preserving_proto_field_name=True))
