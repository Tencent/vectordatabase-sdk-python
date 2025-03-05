from typing import Optional, List, Dict, Any, Union

from tcvectordb import exceptions
from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model import database
from tcvectordb.model.collection_view import CollectionView, Embedding, SplitterProcess, ParsingProcess
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index, IndexField


class AIDatabase:
    """AIDatabase is a vector database system specifically designed for uploading and storing files for AI suites.

    Users can directly upload files to the CollectionView under the AIDatabase,
    which will automatically build a personalized knowledge base.
    """

    def __init__(self,
                 conn: HTTPClient,
                 name: str,
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 info: Optional[dict] = None):
        self.database_name = name
        self.conn = conn
        self._read_consistency = read_consistency
        self.info: Optional[dict] = info
        self.db_type = info.get('dbType', 'AI_DB') if info else 'AI_DB'
        self.collection_count = info.get('count', None) if info else 0

    def get_base_db(self):
        return database.Database(conn=self.conn, name=self.database_name, read_consistency=self._read_consistency)

    def create_database(self, database_name='', timeout: Optional[float] = None):
        """Creates an AI doc database.

        Args:
            database_name (str): The name of the database. A database name can only include
                numbers, letters, and underscores, and must not begin with a letter, and length
                must between 1 and 128
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            AIDatabase: A database object.
        """
        if database_name:
            self.database_name = database_name
        body = {
            'database': self.database_name
        }
        self.conn.post('/ai/database/create', body, timeout)
        return self

    def drop_database(self, database_name='', timeout: Optional[float] = None) -> Dict:
        """Delete a database.

        Args:
            database_name (str): The name of the database to delete.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        if database_name:
            self.database_name = database_name
        body = {
            'database': self.database_name
        }
        res = self.conn.post('/ai/database/drop', body, timeout)
        return res.data()

    def create_collection_view(
            self,
            name: str,
            description: str = '',
            embedding: Optional[Embedding] = None,
            splitter_process: Optional[SplitterProcess] = None,
            index: Optional[Index] = None,
            timeout: Optional[float] = None,
            expected_file_num: Optional[int] = None,
            average_file_size: Optional[int] = None,
            shard: Optional[int] = None,
            replicas: Optional[int] = None,
            parsing_process: Optional[ParsingProcess] = None,
            indexes: List[IndexField] = None,
    ) -> CollectionView:
        """Create a collection view.

        Args:
            name            : The name of the collection view.
            description     : An optional description of the collection view.
            embedding       : Args for embedding.
            splitter_process: Args for splitter process
            index           : A list of the index properties for the documents in a collection.
            timeout         : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.
            expected_file_num: Expected total number of documents
            average_file_size: Estimate the average document size
            shard            : The shard number of the collection.
                               Shard will divide a large dataset into smaller subsets.
            replicas         : The replicas number of the collection.
                               Replicas refers to the number of identical copies of each primary shard,
                               used for disaster recovery and load balancing.
            parsing_process  : Document parsing parameters
            indexes (List[IndexField]): A list of the index properties for the documents in a collection.
        Returns:
            A CollectionView object
        """
        if index is None and indexes:
            index = Index()
            for idx in indexes:
                index.add(idx)
        coll = CollectionView(
            db=self,
            name=name,
            description=description,
            embedding=embedding,
            splitter_process=splitter_process,
            index=index,
            expected_file_num=expected_file_num,
            average_file_size=average_file_size,
            shard=shard,
            replicas=replicas,
            parsing_process=parsing_process,
        )
        self.conn.post('/ai/collectionView/create', vars(coll), timeout)
        return coll

    def describe_collection_view(self,
                                 collection_view_name: str,
                                 timeout: Optional[float] = None) -> CollectionView:
        """Get a CollectionView by name.

        Args:
            collection_view_name: The name of the collection view
            timeout             : An optional duration of time in seconds to allow for the request.
                                  When timeout is set to None, will use the connect timeout.
        Returns:
            A CollectionView object
        """
        if not collection_view_name:
            raise exceptions.ParamError(message='collection_view_name param not found')
        body = {
            'database': self.database_name,
            'collectionView': collection_view_name,
        }
        res = self.conn.post('/ai/collectionView/describe', body, timeout)
        if not res.body['collectionView']:
            raise exceptions.DescribeCollectionException(code=-1, message=str(res.body))
        col = res.body['collectionView']
        coll = CollectionView(
            self,
            col['collectionView'],
        )
        coll.load_fields(col)
        coll.conn_name = collection_view_name
        return coll

    def list_collection_view(self, timeout: Optional[float] = None) -> List[CollectionView]:
        """Get collection view list.

        Args:
            timeout         : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.
        Returns:
            List: all CollectionView objects
        """
        body = {
            'database': self.database_name
        }
        res = self.conn.post('/ai/collectionView/list', body, timeout)
        collections = []
        for col in res.body['collectionViews']:
            coll = CollectionView(
                self,
                col['collectionView'],
            )
            coll.load_fields(col)
            collections.append(coll)
        return collections

    def collection_view(self,
                        collection_view_name: str,
                        timeout: Optional[float] = None) -> CollectionView:
        """Get a CollectionView by name.

        Args:
            collection_view_name (str): The name of the CollectionView .
            timeout (float) : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.

        Returns:
            A CollectionView object
        """
        return self.describe_collection_view(collection_view_name, timeout=timeout)

    def drop_collection_view(self,
                             collection_view_name: str,
                             timeout: Optional[float] = None
                             ) -> Dict:
        """Delete a CollectionView by name.

        Args:
            collection_view_name: The name of the collection view
            timeout             : An optional duration of time in seconds to allow for the request.
                                  When timeout is set to None, will use the connect timeout.
        Returns:
            Dict: Contains code、msg、affectedCount
        """
        if not collection_view_name:
            raise exceptions.ParamError(message='collection_view_name param not found')
        body = {
            'database': self.database_name,
            'collectionView': collection_view_name,
        }
        res = self.conn.post('/ai/collectionView/drop', body, timeout)
        return res.data()

    def truncate_collection_view(self,
                                 collection_view_name: str,
                                 timeout: Optional[float] = None) -> Dict:
        """Clear all data and indexes in the collection view.

        Args:
            collection_view_name: The name of the collection view
            timeout             : An optional duration of time in seconds to allow for the request.
                                  When timeout is set to None, will use the connect timeout.
        Returns:
            Dict: Contains affectedCount
        """
        if not collection_view_name:
            raise exceptions.ParamError(message='collection_view_name param not found')
        body = {
            'database': self.database_name,
            'collectionView': collection_view_name,
        }
        res = self.conn.post('/ai/collectionView/truncate', body, timeout)
        return res.data()

    def set_alias(self,
                  collection_view_name: str,
                  alias: str,
                  ) -> Dict:
        """Set alias for collection view.

        Args:
            collection_view_name: The name of the collection_view.
            alias               : alias name to set.

        Returns:
            Dict: Contains affectedCount
        """
        if not collection_view_name:
            raise exceptions.ParamError(message='collection_view_name param not found')
        if not alias:
            raise exceptions.ParamError(message="alias param not found")
        body = {
            'database': self.database_name,
            'collectionView': collection_view_name,
            'alias': alias
        }
        res = self.conn.post('/ai/alias/set', body)
        return res.data()

    def delete_alias(self, alias: str) -> Dict[str, Any]:
        """Delete alias by name.

        Args:
            alias  : alias name to delete.

        Returns:
            Dict: Contains affectedCount
        """
        if not alias:
            raise exceptions.ParamError(message="alias param not found")
        body = {
            'database': self.database_name,
            'alias': alias
        }
        res = self.conn.post('/ai/alias/delete', body)
        return res.data()
