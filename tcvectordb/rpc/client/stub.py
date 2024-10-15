from typing import Optional, List, Union, Dict
from numpy import ndarray
from requests.adapters import HTTPAdapter

from tcvectordb import VectorDBClient, exceptions
from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.rpc.client.rpcclient import RPCClient
from tcvectordb.rpc.client.vdbclient import VdbClient
from tcvectordb.rpc.model.database import RPCDatabase


class RPCVectorDBClient(VectorDBClient):
    """
    RPCVectorDBClient create a grpc client for database operate.
    """

    def __init__(self,
                 url: str,
                 username='',
                 key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10,
                 proxies: Optional[dict] = None,
                 **kwargs):
        self.url = url
        self.username = username
        self.key = key
        self.timeout = timeout
        self.adapter = adapter
        self.pool_size = pool_size
        self.proxies = proxies
        self.read_consistency = read_consistency
        rpc_client = RPCClient(url=url,
                               username=username,
                               key=key,
                               timeout=timeout,
                               **kwargs)
        self.http: Optional[HTTPClient] = None
        self.vdb_client = VdbClient(client=rpc_client, read_consistency=read_consistency)

    def _get_http(self) -> HTTPClient:
        if not self.http:
            self.http = HTTPClient(url=self.url,
                                   username=self.username,
                                   key=self.key,
                                   timeout=self.timeout,
                                   adapter=self.adapter,
                                   pool_size=self.pool_size,
                                   proxies=self.proxies)
        return self.http

    def create_database(self, database_name: str, timeout: Optional[float] = None) -> RPCDatabase:
        """Create the database if it doesn't exist.

        Args:
            database_name (str): The name of the database. A database name can only include
                numbers, letters, and underscores, and must not begin with a letter, and length
                must between 1 and 128
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            RPCDatabase: A database object.
        """
        return self.vdb_client.create_database(database_name=database_name, timeout=timeout)

    def list_databases(self, timeout: Optional[float] = None) -> List[Union[RPCDatabase, AIDatabase]]:
        return self.vdb_client.list_databases(timeout=timeout)

    def drop_database(self, database_name: str, timeout: Optional[float] = None) -> dict:
        return self.vdb_client.drop_database(database_name=database_name,
                                             timeout=timeout)

    def database(self, database: str) -> Union[RPCDatabase, AIDatabase]:
        """Get database list.

        :param database_name: The name of the database to delete.
        :type  database_name: str

        :return Database object
        :rtype Database
        """
        for db in self.list_databases():
            if db.database_name == database:
                if isinstance(db, AIDatabase):
                    db.conn = self._get_http()
                return db
        raise exceptions.ParamError(message='Database not exist: {}'.format(database))

    def create_ai_database(self, database_name: str, timeout: Optional[float] = None) -> AIDatabase:
        """Creates an AI doc database.

        :param database_name: The name of the database. A database name can only include
        numbers, letters, and underscores, and must not begin with a letter, and length
        must between 1 and 128
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return Database object
        :rtype Database
        """
        db = AIDatabase(conn=self._get_http(), name=database_name, read_consistency=self.read_consistency)
        db.create_database(timeout=timeout)
        return db

    def drop_ai_database(self, database_name: str, timeout: Optional[float] = None):
        """Delete an AI doc database.

        :param database_name: The name of the database to delete.
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
        """
        db = AIDatabase(conn=self._get_http(), name=database_name, read_consistency=self.read_consistency)
        return db.drop_database(timeout=timeout)

    def close(self):
        self.vdb_client.close()
        if self.http:
            self.http.close()

    def exists_collection(self,
                          database_name: str,
                          collection_name: str) -> bool:
        return RPCDatabase(name=database_name,
                           read_consistency=self.vdb_client.read_consistency,
                           vdb_client=self.vdb_client).exists_collection(collection_name)

    def upsert(self,
               database_name: str,
               collection_name: str,
               documents: List[Union[Document, Dict]],
               timeout: Optional[float] = None,
               build_index: bool = True,
               **kwargs):
        return self.vdb_client.upsert(
            database_name=database_name,
            collection_name=collection_name,
            documents=documents,
            timeout=timeout,
            build_index=build_index,
            **kwargs
        )

    def delete(self,
               database_name: str,
               collection_name: str,
               document_ids: List[str] = None,
               filter: Union[Filter, str] = None,
               timeout: Optional[float] = None):
        return self.vdb_client.delete(
            database_name=database_name,
            collection_name=collection_name,
            document_ids=document_ids,
            filter=filter,
            timeout=timeout,
        )

    def update(self,
               database_name: str,
               collection_name: str,
               data: Union[Document, Dict],
               filter: Union[Filter, str] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None):
        return self.vdb_client.update(
            database_name=database_name,
            collection_name=collection_name,
            data=data,
            filter=filter,
            document_ids=document_ids,
            timeout=timeout,
        )

    def query(self,
              database_name: str,
              collection_name: str,
              document_ids: Optional[List] = None,
              retrieve_vector: bool = False,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              filter: Union[Filter, str] = None,
              output_fields: Optional[List[str]] = None,
              timeout: Optional[float] = None,
              ) -> List[Dict]:
        return self.vdb_client.query(
            database_name=database_name,
            collection_name=collection_name,
            document_ids=document_ids,
            retrieve_vector=retrieve_vector,
            limit=limit,
            offset=offset,
            filter=filter,
            output_fields=output_fields,
            timeout=timeout,
        )

    def search(self,
               database_name: str,
               collection_name: str,
               vectors: Union[List[List[float]], ndarray],
               filter: Union[Filter, str] = None,
               params=None,
               retrieve_vector: bool = False,
               limit: int = 10,
               output_fields: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ) -> List[List[Dict]]:
        return self.vdb_client.search(
            database_name=database_name,
            collection_name=collection_name,
            vectors=vectors,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def search_by_id(self,
                     database_name: str,
                     collection_name: str,
                     document_ids: List[str],
                     filter: Union[Filter, str] = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     ) -> List[List[Dict]]:
        return self.vdb_client.search(
            database_name=database_name,
            collection_name=collection_name,
            document_ids=document_ids,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def search_by_text(self,
                       database_name: str,
                       collection_name: str,
                       embedding_items: List[str],
                       filter: Union[Filter, str] = None,
                       params=None,
                       retrieve_vector: bool = False,
                       limit: int = 10,
                       output_fields: Optional[List[str]] = None,
                       timeout: Optional[float] = None,
                       ) -> List[List[Dict]]:
        return self.vdb_client.search(
            database_name=database_name,
            collection_name=collection_name,
            embedding_items=embedding_items,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def hybrid_search(self,
                      database_name: str,
                      collection_name: str,
                      ann: Optional[Union[List[AnnSearch], AnnSearch]] = None,
                      match: Optional[Union[List[KeywordSearch], KeywordSearch]] = None,
                      filter: Union[Filter, str] = None,
                      rerank: Optional[Rerank] = None,
                      retrieve_vector: Optional[bool] = None,
                      output_fields: Optional[List[str]] = None,
                      limit: Optional[int] = None,
                      timeout: Optional[float] = None,
                      **kwargs) -> List[List[Dict]]:
        return self.vdb_client.hybrid_search(
            database_name=database_name,
            collection_name=collection_name,
            ann=ann,
            match=match,
            filter=filter,
            rerank=rerank,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            timeout=timeout,
            **kwargs)
