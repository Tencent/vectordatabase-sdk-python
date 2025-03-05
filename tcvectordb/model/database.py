from typing import List, Optional, Union, Dict, Any

from tcvectordb.model.enum import ReadConsistency

from tcvectordb.client.httpclient import HTTPClient
from tcvectordb import exceptions
from .ai_database import AIDatabase

from .collection import Collection, Embedding, FilterIndexConfig
from .index import Index, IndexField


class Database:
    """Database, Contains Database property and collection API."""

    def __init__(self,
                 conn: Union[HTTPClient, None],
                 name: str = '',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 info: Optional[dict] = None):
        self._dbname = name
        self._conn = conn
        self._read_consistency = read_consistency
        self.info = info
        self.db_type = info.get('dbType', 'BASE_DB') if info else 'BASE_DB'
        self.collection_count = info.get('count', None) if info else 0

    @property
    def conn(self):
        return self._conn

    @property
    def database_name(self):
        return self._dbname

    def create_database(self, database_name='', timeout: Optional[float] = None):
        """Creates a database.

        Args:
            database_name (str): The name of the database. A database name can only include
                numbers, letters, and underscores, and must not begin with a letter, and length
                must between 1 and 128
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Database: A database object.
        """
        if not self.conn:
            raise exceptions.NoConnectError

        if database_name:
            self._dbname = database_name
        if not self.database_name:
            raise exceptions.ParamError(
                message='database name param not found')
        body = {
            'database': self.database_name
        }
        self.conn.post('/database/create', body, timeout)
        return self

    def drop_database(self, database_name='', timeout: Optional[float] = None) -> Dict:
        """Delete a database by name.

        Args:
            database_name (str): The name of the database to delete.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        if not self.conn:
            raise exceptions.NoConnectError
        if database_name:
            self._dbname = database_name
        if not self.database_name:
            raise exceptions.ParamError(
                message='database name param not found')

        body = {
            'database': self.database_name
        }
        try:
            res = self.conn.post('/database/drop', body, timeout)
            return res.data()
        except exceptions.VectorDBException as e:
            if e.message.find('not exist') == -1:
                raise e

    def list_databases(self, timeout: Optional[float] = None) -> List[Union[AIDatabase, "Database"]]:
        """List all databases.

        Args:
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all Database and AIDatabase
        """
        res = self.conn.get('/database/list', timeout=timeout)
        databases = res.body.get('databases', [])
        db_info = res.body.get('info', {})
        res = []
        for db_name in databases:
            info = db_info.get(db_name, {})
            db_type = info.get('dbType', 'BASE_DB')
            if db_type in ('AI_DOC', 'AI_DB'):
                res.append(AIDatabase(conn=self.conn, name=db_name,
                                      read_consistency=self._read_consistency, info=info))
            else:
                res.append(Database(conn=self.conn, name=db_name,
                                    read_consistency=self._read_consistency, info=info))
        return res

    def create_collection(
            self,
            name: str,
            shard: int,
            replicas: int,
            description: str = None,
            index: Index = None,
            embedding: Embedding = None,
            timeout: float = None,
            ttl_config: dict = None,
            filter_index_config: FilterIndexConfig = None,
            indexes: List[IndexField] = None,
    ) -> Collection:
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
            embedding (Embedding): An optional embedding for embedding text when upsert documents.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.
            ttl_config (dict): TTL configuration, when set {'enable': True, 'timeField': 'expire_at'} means
                that ttl is enabled and automatically removed when the time set in the expire_at field expires
            filter_index_config (FilterIndexConfig): Enabling full indexing mode.
                Where all scalar fields are indexed by default.
            indexes (List[IndexField]): A list of the index properties for the documents in a collection.
        Returns:
            A Collection object.
        """
        if not self.database_name:
            raise exceptions.ParamError(message='database not found')
        body = {
            'database': self.database_name,
            'collection': name,
            'shardNum': shard,
            'replicaNum': replicas,
            'embedding': vars(embedding) if embedding else {},
        }
        if description is not None:
            body['description'] = description
        if index is None and indexes:
            index = Index()
            for idx in indexes:
                index.add(idx)
        if index is not None:
            body['indexes'] = index.list()
        if ttl_config is not None:
            body['ttlConfig'] = ttl_config
        if filter_index_config is not None:
            body['filterIndexConfig'] = vars(filter_index_config)
        self._conn.post('/collection/create', body, timeout)
        return Collection(self, name, shard, replicas, description, index, embedding=embedding,
                          ttl_config=ttl_config, filter_index_config=filter_index_config,
                          read_consistency=self._read_consistency)

    def _generate_collection(self, col):
        index = Index()
        for elem in col.pop('indexes', []):
            index.add(**elem)
        ebd = None
        if "embedding" in col:
            ebd = Embedding()
            ebd.set_fields(**col.pop("embedding", {}))
        filter_index_config = None
        if "filterIndexConfig" in col:
            filter_index_config = FilterIndexConfig(**col.pop("filterIndexConfig", {}))
        collection = Collection(
            self,
            name=col.pop('collection', None),
            shard=col.pop('shardNum', None),
            replicas=col.pop('replicaNum', None),
            description=col.pop('description', None),
            index=index,
            embedding=ebd,
            ttl_config=col.pop('ttlConfig', None),
            filter_index_config=filter_index_config,
            read_consistency=self._read_consistency,
            **col,
        )
        return collection

    def list_collections(self, timeout: Optional[float] = None) -> List[Collection]:
        """List all collections in the database.

        Args:
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all Collections
        """
        if not self.database_name:
            raise exceptions.ParamError(message='database not found')
        body = {
            'database': self.database_name
        }
        res = self._conn.post('/collection/list', body, timeout)
        collections = []
        for col in res.body['collections']:
            collection = self._generate_collection(col)
            collections.append(collection)

        return collections

    def describe_collection(self, name: str, timeout: Optional[float] = None) -> Collection:
        """Get a Collection by name.

        Args:
            name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            A Collection object.
        """
        if not self.database_name:
            raise exceptions.ParamError(message='database not found')
        if not name:
            raise exceptions.ParamError(
                message='collection name param not found')
        body = {
            'database': self.database_name,
            'collection': name,
        }
        res = self._conn.post('/collection/describe', body, timeout)
        if not res.body['collection']:
            raise exceptions.DescribeCollectionException(
                code=-1, message=str(res.body))
        col = res.body['collection']
        col = self._generate_collection(col)
        col.conn_name = name
        return col

    def drop_collection(self, name: str, timeout: Optional[float] = None) -> Dict:
        """Delete a collection by name.

        Args:
            name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        if not self.database_name:
            raise exceptions.ParamError(message='database not found')
        if not name:
            raise exceptions.ParamError(
                message='collection name param not found')
        body = {
            'database': self.database_name,
            'collection': name,
        }
        try:
            res = self._conn.post('/collection/drop', body)
            return res.data()
        except exceptions.VectorDBException as e:
            if e.message.find('not exist') == -1:
                raise e

    def truncate_collection(self, collection_name: str) -> Dict:
        """Clear all the data and indexes in the Collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Dict: Contains affectedCount
        """
        if not self.database_name:
            raise exceptions.ParamError(message='param database is blank')
        if not collection_name:
            raise exceptions.ParamError(
                message='collection name param not found')
        body = {
            'database': self.database_name,
            'collection': collection_name,
        }
        res = self._conn.post('/collection/truncate', body)
        return res.data()

    def set_alias(self, collection_name: str, collection_alias: str) -> Dict:
        """Set alias for collection.

        Args:
            collection_name  : The name of the collection.
            collection_alias : alias name to set.
        Returns:
            Dict: Contains affectedCount
        """
        if not self.database_name:
            raise exceptions.ParamError(message='database not found')
        if not collection_name:
            raise exceptions.ParamError(
                message='collection name param not found')
        if not collection_alias:
            raise exceptions.ParamError(message="collection_alias is blank")
        body = {
            'database': self.database_name,
            'collection': collection_name,
            'alias': collection_alias
        }
        postRes = self._conn.post('/alias/set', body)
        if 'affectedCount' in postRes.body:
            return {'affectedCount': postRes.body.get('affectedCount')}
        raise exceptions.ServerInternalError(message='response content is not as expected: {}'.format(postRes.body))

    def delete_alias(self, alias: str) -> Dict[str, Any]:
        """Delete alias by name.

        Args:
            alias  : alias name to delete.

        Returns:
            Dict: Contains affectedCount
        """
        if not self.database_name or not alias:
            raise exceptions.ParamError(message='database and alias required')
        body = {
            'database': self.database_name,
            'alias': alias
        }
        postRes = self._conn.post('/alias/delete', body)
        if 'affectedCount' in postRes.body:
            return {'affectedCount': postRes.body.get('affectedCount')}
        raise exceptions.ServerInternalError(message='response content is not as expected: {}'.format(postRes.body))

    def collection(self, name: str) -> Collection:
        """Get a Collection by name.

        Args:
            name (str): The name of the collection.

        Returns:
            A Collection object
        """
        return self.describe_collection(name)

    def exists_collection(self, collection_name: str) -> bool:
        """Check if the collection exists.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            Bool: True if collection exists else False.
        """
        try:
            self.collection(name=collection_name)
            return True
        except exceptions.ServerInternalError as e:
            if e.code == 15302:
                return False
            raise e

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
                                        indexes: List[IndexField] = None,
                                        ) -> Collection:
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
            indexes (List[IndexField]): A list of the index properties for the documents in a collection.

        Returns:
            Collection: A collection object.
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
            indexes=indexes,
        )
