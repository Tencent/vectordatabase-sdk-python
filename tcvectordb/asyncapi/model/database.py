from typing import List, Optional, Dict, Any, Union

from tcvectordb.asyncapi.model.ai_database import AsyncAIDatabase
from tcvectordb.asyncapi.model.collection import AsyncCollection
from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model.collection import Embedding, Collection
from tcvectordb.model.database import Database
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index


class AsyncDatabase(Database):

    def __init__(self,
                 conn: Union[HTTPClient, None],
                 name: str = '',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 db_type: Optional[str] = None) -> None:
        super().__init__(conn, name, read_consistency, db_type=db_type)

    async def create_database(self, database_name='', timeout: Optional[float] = None):
        super().create_database(database_name, timeout)

    async def drop_database(self, database_name='', timeout: Optional[float] = None):
        return super().drop_database(database_name, timeout)

    async def list_databases(self, timeout: Optional[float] = None) -> List:
        dbs = super().list_databases(timeout)
        return [db_convert(db) for db in dbs]

    async def create_collection(self,
                                name: str,
                                shard: int,
                                replicas: int,
                                description: str = None,
                                index: Index = None,
                                embedding: Embedding = None,
                                timeout: float = None,
                                ) -> AsyncCollection:
        coll = super().create_collection(name,
                                         shard,
                                         replicas,
                                         description,
                                         index,
                                         embedding,
                                         timeout)
        return coll_convert(coll)

    async def list_collections(self, timeout: Optional[float] = None) -> List[AsyncCollection]:
        colls = super().list_collections(timeout)
        return [coll_convert(coll) for coll in colls]

    async def describe_collection(self, name: str, timeout: Optional[float] = None) -> AsyncCollection:
        coll = super().describe_collection(name, timeout)
        return coll_convert(coll)

    async def drop_collection(self, name: str, timeout: Optional[float] = None):
        return super().drop_collection(name, timeout)

    async def truncate_collection(self, collection_name: str) -> Dict[str, Any]:
        return super().truncate_collection(collection_name)

    async def set_alias(self, collection_name: str, collection_alias: str) -> Dict[str, Any]:
        return super().set_alias(collection_name, collection_alias)

    async def delete_alias(self, alias: str) -> Dict[str, Any]:
        return super().delete_alias(alias)

    async def collection(self, name: str) -> AsyncCollection:
        return await self.describe_collection(name)


def db_convert(db) -> Union[AsyncDatabase, AsyncAIDatabase]:
    read_consistency = db.__getattribute__('_read_consistency')
    if isinstance(db, Database):
        return AsyncDatabase(conn=db.conn,
                             name=db.database_name,
                             read_consistency=read_consistency,
                             db_type=db.db_type)
    else:
        return AsyncAIDatabase(conn=db.conn,
                               name=db.database_name,
                               read_consistency=read_consistency,
                               db_type=db.db_type)


def coll_convert(coll: Collection) -> AsyncCollection:
    read_consistency = coll.__getattribute__('_read_consistency')
    a_coll = AsyncCollection(
        db=AsyncDatabase(conn=coll.__getattribute__('_conn'),
                         name=coll.database_name,
                         read_consistency=read_consistency),
        name=coll.collection_name,
        shard=coll.shard,
        replicas=coll.replicas,
        description=coll.description,
        index=coll.index,
        embedding=coll.embedding,
        read_consistency=read_consistency,
        createTime=coll.create_time,
        documentCount=coll.document_count,
        alias=coll.alias,
        indexStatus=coll.index_status,
        **coll.kwargs,
    )
    return a_coll
