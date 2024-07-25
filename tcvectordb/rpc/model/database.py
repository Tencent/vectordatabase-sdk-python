from typing import Union, Optional, List

from cachetools import cached, TTLCache

from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.collection import Collection, Embedding
from tcvectordb.model.database import Database
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index
from tcvectordb.rpc.model.collection import RPCCollection


class RPCDatabase(Database):

    def __init__(self,
                 conn: Union[HTTPClient, None],
                 name: str = '',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 rpc_client=None) -> None:
        super().__init__(conn, name, read_consistency)
        self.rpc_client = rpc_client

    def create_database(self, database_name='', timeout: Optional[float] = None):
        sdb = super().create_database(database_name=database_name, timeout=timeout)
        return db_convert(sdb, self.rpc_client)

    def list_databases(self, timeout: Optional[float] = None) -> List:
        sdbs = super().list_databases(timeout=timeout)
        dbs = []
        for sdb in sdbs:
            if isinstance(sdb, AIDatabase):
                dbs.append(sdb)
            else:
                dbs.append(db_convert(sdb, self.rpc_client))
        return sdbs

    def create_collection(self,
                          name: str,
                          shard: int,
                          replicas: int,
                          description: str,
                          index: Index,
                          embedding: Embedding = None,
                          timeout: float = None,
    ) -> RPCCollection:
        coll = super().create_collection(
            name=name,
            shard=shard,
            replicas=replicas,
            description=description,
            index=index,
            embedding=embedding,
            timeout=timeout,
        )
        return coll_convert(coll, self.rpc_client)

    def list_collections(self, timeout: Optional[float] = None) -> List[RPCCollection]:
        colls = super().list_collections(timeout=timeout)
        res = []
        for coll in colls:
            res.append(coll_convert(coll, self.rpc_client))
        return res

    def describe_collection(self, name: str, timeout: Optional[float] = None) -> RPCCollection:
        coll = super().describe_collection(name=name, timeout=timeout)
        return coll_convert(coll, self.rpc_client)

    @cached(cache=TTLCache(maxsize=1024, ttl=3))
    def collection(self, name: str) -> RPCCollection:
        coll = super().collection(name)
        return coll_convert(coll, self.rpc_client)


def coll_convert(coll: Collection, rpc_client) -> RPCCollection:
    read_consistency = coll.__getattribute__('_read_consistency')
    a_coll = RPCCollection(
        db=RPCDatabase(conn=coll.__getattribute__('_conn'),
                       name=coll.database_name,
                       read_consistency=read_consistency,
                       rpc_client=rpc_client),
        name=coll.collection_name,
        shard=coll.shard,
        replicas=coll.replicas,
        description=coll.description,
        index=coll.index,
        embedding=coll.embedding,
        read_consistency=read_consistency,
        rpc_client=rpc_client,
        createTime=coll.create_time,
        documentCount=coll.document_count,
        alias=coll.alias,
        indexStatus=coll.index_status,
        **coll.kwargs,
    )
    return a_coll


def db_convert(db: Database, rpc_client) -> Union[RPCDatabase, AIDatabase]:
    if isinstance(db, AIDatabase):
        return db
    read_consistency = db.__getattribute__('_read_consistency')
    return RPCDatabase(
        conn=db.conn,
        name=db.database_name,
        read_consistency=read_consistency,
        rpc_client=rpc_client,
    )
