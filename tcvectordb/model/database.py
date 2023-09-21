from typing import List, Optional, Union, Dict, Any

from tcvectordb.model.enum import ReadConsistency

from tcvectordb.client.httpclient import HTTPClient
from tcvectordb import exceptions

from .collection import Collection, Embedding
from .index import Index


class Database:
    def __init__(self,
                 conn: Union[HTTPClient, None],
                 name: str = '',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY) -> None:
        self._dbname = name
        self._conn = conn
        self._read_consistency = read_consistency

    @property
    def conn(self):
        return self._conn

    @property
    def database_name(self):
        return self._dbname

    def create_database(self, database_name='', timeout: Optional[float] = None):
        """Creates a database.

        :param database_name: The name of the database. A database name can only include
        numbers, letters, and underscores, and must not begin with a letter, and length 
        must between 1 and 128
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
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

    def drop_database(self, database_name='', timeout: Optional[float] = None):
        """Delete a database.

        :param database_name: The name of the database to delete.
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
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
            self.conn.post('/database/drop', body, timeout)
        except exceptions.VectorDBException as e:
            if e.message.find('not exist') == -1:
                raise e

    def list_databases(self, timeout: Optional[float] = None) -> List:
        """Get database list.

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return: The database name list
        :rtype: list[str]
        """
        res = self.conn.get('/database/list', timeout=timeout)
        databases = res.body.get('databases', [])
        res = []
        for db in databases:
            res.append(Database(conn=self.conn, name=db, read_consistency=self._read_consistency))
        return res

    def create_collection(
            self,
            name: str,
            shard: int,
            replicas: int,
            description: str,
            index: Index,
            embedding: Embedding = None,
            timeout: Optional[float] = None,
    ) -> Collection:
        """Create a collection.

        :param name: The name of the collection. A collection name can only include
        numbers, letters, and underscores, and must not begin with a letter, and length 
        must between 1 and 128
        :type  name: str

        :param shard: The shard number of the collection. Shard will divide a large dataset into smaller subsets.
        :type shard: int

        :param replicas: The replicas number of the collection. Replicas refers to the number of identical copies
        of each primary shard, used for disaster recovery and load balancing.
        :type replicas: int

        :param description: An optional description of the collection.
        :type description: str

        :param index: A list of the index properties for the documents in a collection.
        :type index: Index class

        :param embedding: An optional embedding for embedding text when upsert documents.
        :type embedding: Embedding class

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return: The Collection object. You can use the collection object to manipulate documents.
        :rtype: Collection class
        """
        if not self.database_name:
            raise exceptions.ParamError(message='database not found')
        if not name:
            raise exceptions.ParamError(
                message='collection name param not found')
        if not index:
            raise exceptions.ParamError(code=-1, message='must set index')

        body = {
            'database': self.database_name,
            'collection': name,
            'shardNum': shard,
            'replicaNum': replicas,
            'description': description,
            'embedding': vars(embedding) if embedding else {},
            'indexes': index.list()
        }
        self._conn.post('/collection/create', body, timeout)

        return Collection(self, name, shard, replicas, description, index, embedding=embedding,
                          read_consistency=self._read_consistency)

    def list_collections(self, timeout: Optional[float] = None) -> List[Collection]:
        """Get collection list.

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return: The database name list
        :rtype: list[Collection]
        """
        if not self.database_name:
            raise exceptions.ParamError(message='database not found')
        body = {
            'database': self.database_name
        }
        res = self._conn.post('/collection/list', body, timeout)
        collections = []
        for col in res.body['collections']:
            index = Index()
            for elem in col.get('indexes', []):
                index.add(**elem)

            ebd = Embedding()
            if "embedding" in col:
                ebd.set_fields(**col.get("embedding"))

            collection = Collection(
                self,
                col['collection'],
                shard=col['shardNum'],
                replicas=col['replicaNum'],
                description=col['description'],
                index=index,
                embedding=ebd,
                create_time=col['createTime'],
                read_consistency=self._read_consistency
            )

            collection.set_fields(**col)

            collections.append(collection)

        return collections

    def describe_collection(self, name: str, timeout: Optional[float] = None) -> Collection:
        """Get a collection details.
        :param name: The name of the collection.
        :type: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return: The Collection object. You can use the collection object to manipulate documents.
        :rtype: Collection class
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
        index = Index()
        for elem in col.get('indexes', []):
            index.add(**elem)

        ebd = Embedding()
        if "embedding" in col:
            ebd.set_fields(**col.get("embedding"))

        collection = Collection(
            self,
            col['collection'],
            shard=col['shardNum'],
            replicas=col['replicaNum'],
            description=col['description'],
            index=index,
            embedding=ebd,
            create_time=col['createTime'],
            read_consistency=self._read_consistency
        )
        collection.set_fields(**col)

        return collection

    def drop_collection(self, name: str, timeout: Optional[float] = None):
        """Delete a collection.
        :param name: The name of the collection.
        :type: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
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
            self._conn.post('/collection/drop', body)
        except exceptions.VectorDBException as e:
            if e.message.find('not exist') == -1:
                raise e

    def truncate_collection(self, collection_name: str) -> Dict[str, Any]:
        if not self.database_name:
            raise exceptions.ParamError(message='param database is blank')
        if not collection_name:
            raise exceptions.ParamError(
                message='collection name param not found')
        body = {
            'database': self.database_name,
            'collection': collection_name,
        }
        try:
            postRes = self._conn.post('/collection/truncate', body)

            if 'affectedCount' in postRes.body:
                return {'affectedCount': postRes.body.get('affectedCount')}

            raise exceptions.ServerInternalError(message='response content is not as expected')

        except exceptions.VectorDBException as e:
            if e.message.find('not exist') == -1:
                raise e

    def set_alias(self, collection_name: str, collection_alias: str) -> Dict[str, Any]:
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

        try:
            postRes = self._conn.post('/alias/set', body)

            if 'affectedCount' in postRes.body:
                return {'affectedCount': postRes.body.get('affectedCount')}

            raise exceptions.ServerInternalError(message='response content is not as expected')
        except exceptions.VectorDBException as e:
            if e.message.find('not exist') == -1:
                raise e

    def delete_alias(self, alias: str) -> Dict[str, Any]:
        if not self.database_name or not alias:
            raise exceptions.ParamError(message='database and alias required')

        body = {
            'database': self.database_name,
            'alias': alias
        }

        try:
            postRes = self._conn.post('/alias/delete', body)

            if 'affectedCount' in postRes.body:
                return {'affectedCount': postRes.body.get('affectedCount')}

            raise exceptions.ServerInternalError(message='response content is not as expected')
        except exceptions.VectorDBException as e:
            if e.message.find('not exist') == -1:
                raise e

    def collection(self, name: str) -> Collection:
        """Get a collection object, same as describe_collection.
        :param name: The name of the collection.
        :type: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return: The Collection object. You can use the collection object to manipulate documents.
        :rtype: Collection class
        """
        return self.describe_collection(name)
