from typing import Optional, List, Dict, Any

from tcvectordb.asyncapi.model.collection_view import AsyncCollectionView
from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.collection_view import SplitterProcess, Embedding, CollectionView, ParsingProcess
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index


class AsyncAIDatabase(AIDatabase):
    """Async wrap of AIDatabase"""

    def __init__(self,
                 conn: HTTPClient,
                 name: str,
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 info: Optional[dict] = None):
        super().__init__(conn, name, read_consistency, info=info)

    async def create_database(self, database_name='', timeout: Optional[float] = None):
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

    async def create_collection_view(
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
    ) -> AsyncCollectionView:
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
        Returns:
            A AsyncCollectionView object
        """
        cv = super().create_collection_view(name=name,
                                            description=description,
                                            embedding=embedding,
                                            splitter_process=splitter_process,
                                            index=index,
                                            timeout=timeout,
                                            expected_file_num=expected_file_num,
                                            average_file_size=average_file_size,
                                            shard=shard,
                                            replicas=replicas,
                                            parsing_process=parsing_process,
                                            )
        return cv_convert(cv)

    async def describe_collection_view(self,
                                       collection_view_name: str,
                                       timeout: Optional[float] = None) -> AsyncCollectionView:
        """Get a CollectionView by name.

        Args:
            collection_view_name: The name of the collection view
            timeout             : An optional duration of time in seconds to allow for the request.
                                  When timeout is set to None, will use the connect timeout.
        Returns:
            A AsyncCollectionView object
        """
        cv = super().describe_collection_view(collection_view_name, timeout)
        acv = cv_convert(cv)
        acv.conn_name = collection_view_name,
        return acv

    async def list_collection_view(self, timeout: Optional[float] = None) -> List[AsyncCollectionView]:
        """Get collection view list.

        Args:
            timeout         : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.
        Returns:
            List: all AsyncCollectionView objects
        """
        cvs = super().list_collection_view(timeout)
        return [cv_convert(cv) for cv in cvs]

    async def collection_view(self,
                              collection_view_name: str,
                              timeout: Optional[float] = None) -> AsyncCollectionView:
        """Get a CollectionView by name.

        Args:
            collection_view_name (str): The name of the CollectionView .
            timeout (float) : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.

        Returns:
            A CollectionView object
        """
        return await self.describe_collection_view(collection_view_name, timeout)

    async def drop_collection_view(self,
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
        return super().drop_collection_view(collection_view_name, timeout)

    async def truncate_collection_view(self,
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
        return super().truncate_collection_view(collection_view_name, timeout)

    async def set_alias(self,
                        collection_view_name: str,
                        alias: str,
                        ) -> Dict[str, Any]:
        """Set alias for collection view.

        Args:
            collection_view_name: The name of the collection_view.
            alias               : alias name to set.

        Returns:
            Dict: Contains affectedCount
        """
        return super().set_alias(collection_view_name, alias)

    async def delete_alias(self, alias: str) -> Dict[str, Any]:
        """Delete alias by name.

        Args:
            alias  : alias name to delete.

        Returns:
            Dict: Contains affectedCount
        """
        return super().delete_alias(alias)


def cv_convert(coll: CollectionView) -> AsyncCollectionView:
    return AsyncCollectionView(
        db=coll.db,
        name=coll.name,
        description=coll.description,
        embedding=coll.embedding,
        splitter_process=coll.splitter_process,
        index=coll.index,
        expected_file_num=coll.expected_file_num,
        average_file_size=coll.average_file_size,
        shard=coll.shard,
        replicas=coll.replicas,
        parsing_process=coll.parsing_process,
    )
