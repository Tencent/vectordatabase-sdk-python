from typing import List, Optional, Union

from tcvectordb.client.httpclient import HTTPClient
from tcvectordb import exceptions

from .collection import Collection
from .index import Index


class Database:
    def __init__(self, conn: Union[HTTPClient, None], name: str = '') -> None:
        self._dbname = name
        self._conn = conn

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
            res.append(Database(conn=self.conn, name=db))
        return res

    def create_collection(
        self,
        name: str,
        shard: int,
        replicas: int,
        description: str,
        index: Index,
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
            'indexes': index.list()
        }
        self._conn.post('/collection/create', body, timeout)

        return Collection(self, name, shard, replicas, description, index)

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
        res = self._conn.post('/collection/list', body)
        collections = []
        for col in res.body['collections']:
            index = Index()
            for elem in col.get('indexes', []):
                index.add(**elem)
            collection = Collection(
                self,
                col['collection'],
                shard=col['shardNum'],
                replicas=col['replicaNum'],
                description=col['description'],
                index=index,
                create_time=col['createTime'],
            )
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
        res = self._conn.post('/collection/describe', body)
        if not res.body['collection']:
            raise exceptions.DescribeCollectionException(
                code=-1, message=str(res.body))
        col = res.body['collection']
        index = Index()
        for elem in col.get('indexes', []):
            index.add(**elem)

        collection = Collection(
            self,
            col['collection'],
            shard=col['shardNum'],
            replicas=col['replicaNum'],
            description=col['description'],
            index=index,
            create_time=col['createTime'],
        )
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
