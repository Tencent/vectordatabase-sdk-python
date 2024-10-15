from typing import Optional, List, Dict, Any

from cachetools import cached, TTLCache

from tcvectordb.model.collection import Embedding
from tcvectordb.model.database import Database
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index
from tcvectordb.rpc.model.collection import RPCCollection


class RPCDatabase(Database):

    def __init__(self,
                 name: str = '',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 vdb_client=None,
                 db_type: Optional[str] = None) -> None:
        super().__init__(None, name, read_consistency, db_type=db_type)
        self.vdb_client = vdb_client

    def create_database(self, database_name='', timeout: Optional[float] = None):
        return self.vdb_client.create_database(database_name=database_name, timeout=timeout)

    def drop_database(self, database_name='', timeout: Optional[float] = None) -> dict:
        return self.vdb_client.drop_database(database_name=database_name,
                                             timeout=timeout)

    def list_databases(self, timeout: Optional[float] = None) -> List:
        return self.vdb_client.list_databases(timeout=timeout)

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
        return self.vdb_client.create_collection(
            database_name=self.database_name,
            collection_name=name,
            shard=shard,
            replicas=replicas,
            description=description,
            index=index,
            embedding=embedding,
            timeout=timeout,
            ttl_config=ttl_config,
        )

    def list_collections(self, timeout: Optional[float] = None) -> List[RPCCollection]:
        return self.vdb_client.list_collections(database_name=self.database_name, timeout=timeout)

    def describe_collection(self, name: str, timeout: Optional[float] = None) -> RPCCollection:
        return self.vdb_client.describe_collection(database_name=self.database_name,
                                                   collection_name=name,
                                                   timeout=timeout)

    def drop_collection(self, name: str, timeout: Optional[float] = None) -> dict:
        return self.vdb_client.drop_collection(database_name=self.database_name,
                                               collection_name=name,
                                               timeout=timeout)

    def truncate_collection(self, collection_name: str) -> dict:
        return self.vdb_client.truncate_collection(database_name=self.database_name,
                                                   collection_name=collection_name)

    def set_alias(self, collection_name: str, collection_alias: str) -> Dict[str, Any]:
        return self.vdb_client.set_alias(database_name=self.database_name,
                                         collection_name=collection_name,
                                         collection_alias=collection_alias)

    def delete_alias(self, alias: str) -> Dict[str, Any]:
        return self.vdb_client.delete_alias(database_name=self.database_name,
                                            alias=alias)

    @cached(cache=TTLCache(maxsize=1024, ttl=3))
    def collection(self, name: str) -> RPCCollection:
        return self.describe_collection(name=name)
