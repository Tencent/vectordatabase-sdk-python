from typing import List, Optional, Dict, Any, Union

from tcvectordb.asyncapi.model.ai_database import AsyncAIDatabase
from tcvectordb.asyncapi.model.collection import AsyncCollection
from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model.collection import Embedding, Collection, FilterIndexConfig
from tcvectordb.model.database import Database
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index


class AsyncDatabase(Database):
    """AsyncDatabase, Contains Database property and collection async API."""

    def __init__(self,
                 conn: Union[HTTPClient, None],
                 name: str = '',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 info: Optional[dict] = None) -> None:
        super().__init__(conn, name, read_consistency, info=info)

    async def create_database(self, database_name='', timeout: Optional[float] = None):
        """Creates a database.

        Args:
            database_name (str): The name of the database. A database name can only include
                numbers, letters, and underscores, and must not begin with a letter, and length
                must between 1 and 128
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            AsyncDatabase: A database object for async api.
        """
        return super().create_database(database_name, timeout)

    async def drop_database(self, database_name='', timeout: Optional[float] = None) -> Dict:
        """Delete a database.

        Args:
            database_name (str): The name of the database to delete.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        return super().drop_database(database_name, timeout)

    async def list_databases(self, timeout: Optional[float] = None) -> List[Union["AsyncDatabase", AsyncAIDatabase]]:
        """List all databases.

        Args:
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all AsyncDatabase and AsyncAIDatabase
        """
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
                                ttl_config: dict = None,
                                filter_index_config: FilterIndexConfig = None,
                                ) -> AsyncCollection:
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
            A AsyncCollection object.
        """
        coll = super().create_collection(name,
                                         shard,
                                         replicas,
                                         description,
                                         index,
                                         embedding,
                                         timeout,
                                         ttl_config=ttl_config,
                                         filter_index_config=filter_index_config)
        return coll_convert(coll)

    async def create_collection_if_not_exists(self,
                                              name: str,
                                              shard: int,
                                              replicas: int,
                                              description: str = None,
                                              index: Index = None,
                                              embedding: Embedding = None,
                                              timeout: float = None,
                                              ttl_config: dict = None,
                                              filter_index_config: FilterIndexConfig = None,
                                              ) -> AsyncCollection:
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
            AsyncCollection: A collection object.
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
            filter_index_config=filter_index_config,
        )
        return coll_convert(coll)

    async def list_collections(self, timeout: Optional[float] = None) -> List[AsyncCollection]:
        """List all collections in the database.

        Args:
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all AsyncCollection
        """
        colls = super().list_collections(timeout)
        return [coll_convert(coll) for coll in colls]

    async def describe_collection(self, name: str, timeout: Optional[float] = None) -> AsyncCollection:
        """Get a Collection by name.

        Args:
            name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            A AsyncCollection object.
        """
        coll = super().describe_collection(name, timeout)
        acoll = coll_convert(coll)
        acoll.conn_name = name
        return acoll

    async def drop_collection(self, name: str, timeout: Optional[float] = None) -> Dict:
        """Delete a collection by name.

        Args:
            name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        return super().drop_collection(name, timeout)

    async def truncate_collection(self, collection_name: str) -> Dict:
        """Clear all the data and indexes in the Collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Dict: Contains affectedCount
        """
        return super().truncate_collection(collection_name)

    async def set_alias(self, collection_name: str, collection_alias: str) -> Dict:
        """Set alias for collection.

        Args:
            collection_name  : The name of the collection.
            collection_alias : alias name to set.
        Returns:
            Dict: Contains affectedCount
        """
        return super().set_alias(collection_name, collection_alias)

    async def delete_alias(self, alias: str) -> Dict[str, Any]:
        """Delete alias by name.

        Args:
            alias  : alias name to delete.

        Returns:
            Dict: Contains affectedCount
        """
        return super().delete_alias(alias)

    async def collection(self, name: str) -> AsyncCollection:
        """Get a Collection by name.

        Args:
            name (str): The name of the collection.

        Returns:
            A AsyncCollection object
        """
        return await self.describe_collection(name)


def db_convert(db) -> Union[AsyncDatabase, AsyncAIDatabase]:
    read_consistency = db.__getattribute__('_read_consistency')
    if isinstance(db, Database):
        return AsyncDatabase(conn=db.conn,
                             name=db.database_name,
                             read_consistency=read_consistency,
                             info=db.info)
    else:
        return AsyncAIDatabase(conn=db.conn,
                               name=db.database_name,
                               read_consistency=read_consistency,
                               info=db.info)


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
        ttl_config=coll.ttl_config,
        filter_index_config=coll.filter_index_config,
        createTime=coll.create_time,
        documentCount=coll.document_count,
        alias=coll.alias,
        indexStatus=coll.index_status,
        **coll.kwargs,
    )
    return a_coll
