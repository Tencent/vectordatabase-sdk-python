from typing import List, Optional, Union, Dict, Any

from numpy import ndarray
from requests.adapters import HTTPAdapter

from tcvectordb import VectorDBClient, exceptions
from tcvectordb.asyncapi.model.ai_database import AsyncAIDatabase
from tcvectordb.asyncapi.model.database import AsyncDatabase
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from tcvectordb.model.enum import ReadConsistency


class AsyncVectorDBClient(VectorDBClient):

    def __init__(self,
                 url=None,
                 username='',
                 key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10,
                 proxies: Optional[dict] = None):
        super().__init__(url, username, key, read_consistency, timeout, adapter,
                         pool_size=pool_size, proxies=proxies)

    async def create_database(self, database_name: str, timeout: Optional[float] = None) -> AsyncDatabase:
        db = AsyncDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        await db.create_database(timeout=timeout)
        return db

    async def create_database_if_not_exists(self, database_name: str,
                                            timeout: Optional[float] = None,
                                            ) -> AsyncDatabase:
        """Create the database if it doesn't exist.

        Args:
            database_name (str): The name of the database. A database name can only include
                numbers, letters, and underscores, and must not begin with a letter, and length
                must between 1 and 128
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            AsyncDatabase: A database object.
        """
        db = AsyncDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        super().create_database_if_not_exists(database_name, timeout)
        return db

    async def create_ai_database(self, database_name: str, timeout: Optional[float] = None) -> AsyncAIDatabase:
        db = AsyncAIDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        await db.create_database(timeout=timeout)
        return db

    async def drop_database(self, database_name: str, timeout: Optional[float] = None):
        return super().drop_database(database_name, timeout)

    async def drop_ai_database(self, database_name: str, timeout: Optional[float] = None):
        return super().drop_ai_database(database_name, timeout)

    async def list_databases(self, timeout: Optional[float] = None) -> List[Union[AsyncDatabase, AsyncAIDatabase]]:
        db = AsyncDatabase(conn=self._conn, read_consistency=self._read_consistency)
        dbs = await db.list_databases(timeout=timeout)
        return dbs

    async def database(self, database: str) -> Union[AsyncDatabase, AsyncAIDatabase]:
        dbs = await self.list_databases()
        for db in dbs:
            if db.database_name == database:
                return db
        raise exceptions.ParamError(message='Database not exist: {}'.format(database))

    async def upsert(self,
                     database_name: str,
                     collection_name: str,
                     documents: List[Union[Document, Dict]],
                     timeout: Optional[float] = None,
                     build_index: bool = True,
                     **kwargs):
        return super().upsert(
            database_name=database_name,
            collection_name=collection_name,
            documents=documents,
            timeout=timeout,
            build_index=build_index,
            **kwargs)

    async def delete(self,
                     database_name: str,
                     collection_name: str,
                     document_ids: List[str] = None,
                     filter: Union[Filter, str] = None,
                     timeout: Optional[float] = None):
        return super().delete(
            database_name=database_name,
            collection_name=collection_name,
            document_ids=document_ids,
            filter=filter,
            timeout=timeout,
        )

    async def update(self,
                     database_name: str,
                     collection_name: str,
                     data: Union[Document, Dict],
                     filter: Union[Filter, str] = None,
                     document_ids: Optional[List[str]] = None,
                     timeout: Optional[float] = None):
        return super().update(
            database_name=database_name,
            collection_name=collection_name,
            data=data,
            filter=filter,
            document_ids=document_ids,
            timeout=timeout,
        )

    async def query(self,
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
        return super().query(
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

    async def search(self,
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
        return super().search(
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

    async def search_by_id(self,
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
        return super().search_by_id(
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

    async def search_by_text(self,
                             database_name: str,
                             collection_name: str,
                             embedding_items: List[str],
                             filter: Union[Filter, str] = None,
                             params=None,
                             retrieve_vector: bool = False,
                             limit: int = 10,
                             output_fields: Optional[List[str]] = None,
                             timeout: Optional[float] = None,
                             ) -> Dict[str, Any]:
        return super().search_by_text(
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

    async def hybrid_search(self,
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
        return super().hybrid_search(
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
