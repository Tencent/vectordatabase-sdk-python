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
                 **kwargs):
        options = [
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
        ]
        self.channel = grpc.insecure_channel(self._address(url), options=options)
        self.stub = olama_pb2_grpc.SearchEngineStub(self.channel)
        if password is None:
            password = key
        authorization = 'Bearer account={0}&api_key={1}'.format(username, password)
        self.headers = [('authorization', authorization)]
        self.timeout = timeout
        self.direct = False

    def close(self):
        self.channel.close()

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
            ret: olama_pb2.UpsertResponse = self.stub.upsert(
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
            ret: olama_pb2.SearchResponse = self.stub.search(
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
            ret: olama_pb2.SearchResponse = self.stub.hybrid_search(
                req, metadata=self._get_headers(ai), timeout=timeout)
            self._result_check(ret, ret.warning)
            return ret
        except ServerInternalError as se:
            raise se
        except Exception as e:
            raise GrpcException(message=str(e))

    def keyword_search(self,
                       req: olama_pb2.SearchRequest,
                       timeout: Optional[float] = None) -> olama_pb2.SearchResponse:
        self._print_req(req)
        if timeout is None:
            timeout = self.timeout
        try:
            ret: olama_pb2.SearchResponse = self.stub.keyword_search(
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
            ret: olama_pb2.QueryResponse = self.stub.query(
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
            ret: olama_pb2.DeleteResponse = self.stub.dele(
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
            ret: olama_pb2.UpdateResponse = self.stub.update(
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
            ret: olama_pb2.ExplainResponse = self.stub.explain(
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
            ret: olama_pb2.CountResponse = self.stub.count(
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
            ret: olama_pb2.DatabaseResponse = self.stub.createDatabase(
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
            ret: olama_pb2.DatabaseResponse = self.stub.dropDatabase(
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
            ret: olama_pb2.DatabaseResponse = self.stub.listDatabases(
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
            ret: olama_pb2.UpdateAliasResponse = self.stub.setAlias(
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
            ret: olama_pb2.UpdateAliasResponse = self.stub.deleteAlias(
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
            ret: olama_pb2.RebuildIndexResponse = self.stub.rebuildIndex(
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
            ret: olama_pb2.AddIndexResponse = self.stub.addIndex(
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
            ret: olama_pb2.ModifyVectorIndexResponse = self.stub.modifyVectorIndex(
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
            ret: olama_pb2.CreateCollectionResponse = self.stub.createCollection(
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
            ret: olama_pb2.DropCollectionResponse = self.stub.dropCollection(
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
            ret: olama_pb2.ListCollectionsResponse = self.stub.listCollections(
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
            ret: olama_pb2.DescribeCollectionResponse = self.stub.describeCollection(
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
            ret: olama_pb2.TruncateCollectionResponse = self.stub.truncateCollection(
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
            ret: olama_pb2.UserAccountResponse = self.stub.user_create(
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
            ret: olama_pb2.UserPrivilegesResponse = self.stub.user_grant(
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
            ret: olama_pb2.UserPrivilegesResponse = self.stub.user_revoke(
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
            ret: olama_pb2.UserDescribeResponse = self.stub.user_describe(
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
            ret: olama_pb2.UserListResponse = self.stub.user_list(
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
            ret: olama_pb2.UserAccountResponse = self.stub.user_drop(
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
            ret: olama_pb2.UserAccountResponse = self.stub.user_change_password(
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
