from typing import Optional, List, Dict, Any, Union

from cachetools import cached, TTLCache

from tcvectordb.model.ai_database import AIDatabase

from tcvectordb import exceptions
from tcvectordb.model.collection import Embedding, FilterIndexConfig
from tcvectordb.model.database import Database
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index
from tcvectordb.rpc.model.collection import RPCCollection


class RPCDatabase(Database):
    """RPCDatabase, Contains Database property and collection rpc API."""

    def __init__(self,
                 name: str = '',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 vdb_client=None,
                 info: Optional[dict] = None) -> None:
        super().__init__(None, name, read_consistency, info=info)
        self.vdb_client = vdb_client

    def create_database(self, database_name='', timeout: Optional[float] = None):
        """Create a database.

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

    def drop_database(self, database_name='', timeout: Optional[float] = None) -> Dict:
        """Delete a database.

        Args:
            database_name (str): The name of the database to delete.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        return self.vdb_client.drop_database(database_name=database_name,
                                             timeout=timeout)

    def list_databases(self, timeout: Optional[float] = None) -> List[Union["RPCDatabase", AIDatabase]]:
        """List all databases.

        Args:
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all RPCDatabase and AIDatabase
        """
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
                          filter_index_config: FilterIndexConfig = None,
                          ) -> RPCCollection:
        """Create a collection.

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
            filter_index_config (FilterIndexConfig): Enabling full indexing mode.
                Where all scalar fields are indexed by default.

        Returns:
            A RPCCollection object.
        """
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
            filter_index_config=filter_index_config,
        )

    def list_collections(self, timeout: Optional[float] = None) -> List[RPCCollection]:
        """List all collections in the database.

        Args:
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all RPCCollection
        """
        return self.vdb_client.list_collections(database_name=self.database_name, timeout=timeout)

    def describe_collection(self, name: str, timeout: Optional[float] = None) -> RPCCollection:
        """Get a Collection by name.

        Args:
            name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            A RPCCollection object.
        """
        return self.vdb_client.describe_collection(database_name=self.database_name,
                                                   collection_name=name,
                                                   timeout=timeout)

    def drop_collection(self, name: str, timeout: Optional[float] = None) -> Dict:
        """Delete a collection by name.

        Args:
            name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        return self.vdb_client.drop_collection(database_name=self.database_name,
                                               collection_name=name,
                                               timeout=timeout)

    def truncate_collection(self, collection_name: str) -> Dict:
        """Clear all the data and indexes in the Collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Dict: Contains affectedCount
        """
        return self.vdb_client.truncate_collection(database_name=self.database_name,
                                                   collection_name=collection_name)

    def set_alias(self, collection_name: str, collection_alias: str) -> Dict:
        """Set alias for collection.

        Args:
            collection_name  : The name of the collection.
            collection_alias : alias name to set.
        Returns:
            Dict: Contains affectedCount
        """
        return self.vdb_client.set_alias(database_name=self.database_name,
                                         collection_name=collection_name,
                                         collection_alias=collection_alias)

    def delete_alias(self, alias: str) -> Dict[str, Any]:
        """Delete alias by name.

        Args:
            alias  : alias name to delete.

        Returns:
            Dict: Contains affectedCount
        """
        return self.vdb_client.delete_alias(database_name=self.database_name,
                                            alias=alias)

    @cached(cache=TTLCache(maxsize=1024, ttl=3))
    def collection(self, name: str) -> RPCCollection:
        """Get a Collection by name.

        Args:
            name (str): The name of the collection.

        Returns:
            A RPCCollection object
        """
        return self.describe_collection(name=name)

    def create_collection_if_not_exists(self,
                                        name: str,
                                        shard: int,
                                        replicas: int,
                                        description: str = None,
                                        index: Index = None,
                                        embedding: Embedding = None,
                                        timeout: float = None,
                                        ttl_config: dict = None,
                                        filter_index_config: FilterIndexConfig = None,
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
            filter_index_config (FilterIndexConfig): Enabling full indexing mode.
                Where all scalar fields are indexed by default.

        Returns:
            RPCCollection: A collection object.
        """
        try:
            return self.collection(name=name)
        except exceptions.ServerInternalError as e:
            if e.code != 15302:
                raise e
        return self.create_collection(
            name=name,
            shard=shard,
            replicas=replicas,
            description=description,
            index=index,
            embedding=embedding,
            timeout=timeout,
            ttl_config=ttl_config,
            filter_index_config=filter_index_config,
        )
