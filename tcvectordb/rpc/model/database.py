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
                 vdb_client=None,
                 db_type: Optional[str] = None) -> None:
        super().__init__(conn, name, read_consistency, db_type=db_type)
        self.vdb_client = vdb_client

    def create_database(self, database_name='', timeout: Optional[float] = None):
        sdb = super().create_database(database_name=database_name, timeout=timeout)
        return db_convert(sdb, self.vdb_client)

    def list_databases(self, timeout: Optional[float] = None) -> List:
        sdbs = super().list_databases(timeout=timeout)
        dbs = []
        for sdb in sdbs:
            if isinstance(sdb, AIDatabase):
                dbs.append(sdb)
            else:
                dbs.append(db_convert(sdb, self.vdb_client))
        return sdbs

    def create_collection(self,
                          name: str,
                          shard: int,
                          replicas: int,
                          description: str = None,
                          index: Index = None,
                          embedding: Embedding = None,
                          timeout: float = None,
                          ttl_config: dict = None,
    ) -> RPCCollection:
        coll = super().create_collection(
            name=name,
            shard=shard,
            replicas=replicas,
            description=description,
            index=index,
            embedding=embedding,
            timeout=timeout,
            ttl_config=ttl_config,
        )
        return coll_convert(coll, self.vdb_client)

    def create_collection_if_not_exists(self,
                                        name: str,
                                        shard: int,
                                        replicas: int,
                                        description: str = None,
                                        index: Index = None,
                                        embedding: Embedding = None,
                                        timeout: float = None,
                                        ttl_config: dict = None,
                                        ) -> RPCCollection:
        """Create the collection if it doesn't exist.

        Args:
            name (str): The name of the collection. A collection name can only include
                numbers, letters, and underscores, and must not begin with a letter, and length
                must between 1 and 128
            shard (int): The shard number of the collection. Shard will divide a large dataset into smaller subsets.
            replicas (int): The replicas number of the collection. Replicas refers to the number of identical copies
                of each primary shard, used for disaster recovery and load balancing.
            description (str): An optional description of the collection.
            index (Index): A list of the index properties for the documents in a collection.
            embedding (``Embedding``): An optional embedding for embedding text when upsert documents.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.
            ttl_config (dict): TTL configuration, when set {'enable': True, 'timeField': 'expire_at'} means
                that ttl is enabled and automatically removed when the time set in the expire_at field expires

        Returns:
            RPCCollection: A collection object.
        """
        coll = super().create_collection_if_not_exists(
            name=name,
            shard=shard,
            replicas=replicas,
            description=description,
            index=index,
            embedding=embedding,
            timeout=timeout,
            ttl_config=ttl_config,
        )
        return coll_convert(coll, self.vdb_client)

    def list_collections(self, timeout: Optional[float] = None) -> List[RPCCollection]:
        colls = super().list_collections(timeout=timeout)
        res = []
        for coll in colls:
            res.append(coll_convert(coll, self.vdb_client))
        return res

    def describe_collection(self, name: str, timeout: Optional[float] = None) -> RPCCollection:
        coll = super().describe_collection(name=name, timeout=timeout)
        return coll_convert(coll, self.vdb_client)

    @cached(cache=TTLCache(maxsize=1024, ttl=3))
    def collection(self, name: str) -> RPCCollection:
        coll = super().collection(name)
        return coll_convert(coll, self.vdb_client)


def coll_convert(coll: Collection, vdb_client) -> RPCCollection:
    read_consistency = coll.__getattribute__('_read_consistency')
    a_coll = RPCCollection(
        db=RPCDatabase(conn=coll.__getattribute__('_conn'),
                       name=coll.database_name,
                       read_consistency=read_consistency,
                       vdb_client=vdb_client),
        name=coll.collection_name,
        shard=coll.shard,
        replicas=coll.replicas,
        description=coll.description,
        index=coll.index,
        embedding=coll.embedding,
        read_consistency=read_consistency,
        ttl_config=coll.ttl_config,
        vdb_client=vdb_client,
        createTime=coll.create_time,
        documentCount=coll.document_count,
        alias=coll.alias,
        indexStatus=coll.index_status,
        **coll.kwargs,
    )
    return a_coll


def db_convert(db: Database, vdb_client) -> Union[RPCDatabase, AIDatabase]:
    if isinstance(db, AIDatabase):
        return db
    if isinstance(db, RPCDatabase):
        return db
    read_consistency = db.__getattribute__('_read_consistency')
    return RPCDatabase(
        conn=db.conn,
        name=db.database_name,
        read_consistency=read_consistency,
        vdb_client=vdb_client,
        db_type=db.db_type,
    )
