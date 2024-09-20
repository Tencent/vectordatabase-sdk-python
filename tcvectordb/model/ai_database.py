from typing import Optional, List, Dict, Any

from tcvectordb import exceptions
from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model import database
from tcvectordb.model.collection_view import CollectionView, Embedding, SplitterProcess
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index


class AIDatabase:
    """AIDatabase and about CollectionView operating."""

    def __init__(self,
                 conn: HTTPClient,
                 name: str,
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 db_type: Optional[str] = None):
        self.database_name = name
        self.conn = conn
        self._read_consistency = read_consistency
        self.db_type = db_type

    def get_base_db(self):
        return database.Database(conn=self.conn, name=self.database_name, read_consistency=self._read_consistency)

    def create_database(self, database_name='', timeout: Optional[float] = None):
        """Creates an AI Database.

        Args:
            database_name: database's name to create.
            timeout      : An optional duration of time in seconds to allow for the request.
                           When timeout is set to None, will use the connect timeout.
        """
        if database_name:
            self.database_name = database_name
        body = {
            'database': self.database_name
        }
        self.conn.post('/ai/database/create', body, timeout)

    def drop_database(self, database_name='', timeout: Optional[float] = None) -> Dict[str, Any]:
        """Delete an AI database.

        Args:
            database_name: database's name to drop.
            timeout      : An optional duration of time in seconds to allow for the request.
                           When timeout is set to None, will use the connect timeout.
        Returns:
            affectedCount: affected count in dict
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
        Returns:
            CollectionView
        """
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
        )
        self.conn.post('/ai/collectionView/create', vars(coll), timeout)
        return coll

    def describe_collection_view(self,
                                 collection_view_name: str,
                                 timeout: Optional[float] = None) -> CollectionView:
        """Get a collection view details.

        Args:
            collection_view_name: The name of the collection view
            timeout             : An optional duration of time in seconds to allow for the request.
                                  When timeout is set to None, will use the connect timeout.
        Returns:
            CollectionView
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
        return coll

    def list_collection_view(self, timeout: Optional[float] = None) -> List[CollectionView]:
        """Get collection view list.

        Args:
            timeout         : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.
        Returns:
            list[CollectionView]
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
        """Get a CollectionView object, same as describe_collection_view."""
        return self.describe_collection_view(collection_view_name, timeout=timeout)

    def drop_collection_view(self,
                             collection_view_name: str,
                             timeout: Optional[float] = None
                             ) -> Dict[str, Any]:
        """Delete a collection view.

        Args:
            collection_view_name: The name of the collection view
            timeout             : An optional duration of time in seconds to allow for the request.
                                  When timeout is set to None, will use the connect timeout.
        Returns:
            affectedCount: affected count in dict
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
                                 timeout: Optional[float] = None) -> Dict[str, Any]:
        """Clear all data and indexes in the collection view.

        Args:
            collection_view_name: The name of the collection view
            timeout             : An optional duration of time in seconds to allow for the request.
                                  When timeout is set to None, will use the connect timeout.
        Returns:
            affectedCount: affected count in dict
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
                  ) -> Dict[str, Any]:
        """Set alias for collection view.

        Args:
            collection_view_name: collection_view's name.
            alias               : alias name to set.
        Returns:
            affectedCount: affected count in dict
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
        """Delete alias.
        Args:
            alias  : alias name to delete.
        Returns:
            affectedCount: affected count in dict
        """
        if not alias:
            raise exceptions.ParamError(message="alias param not found")
        body = {
            'database': self.database_name,
            'alias': alias
        }
        res = self.conn.post('/ai/alias/delete', body)
        return res.data()
