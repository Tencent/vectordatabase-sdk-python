from typing import List, Optional, Union, Dict, Any

from numpy import ndarray
from requests.adapters import HTTPAdapter

from tcvectordb.model.enum import ReadConsistency

from .httpclient import HTTPClient
from tcvectordb.model.database import Database
from tcvectordb import exceptions
from tcvectordb.model.ai_database import AIDatabase
from ..model.collection import Collection
from ..model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from ..model.index import FilterIndex


class VectorDBClient:
    """Client for vector db.

    Connect with the database instance using HTTP.
    """

    def __init__(self, url=None, username='', key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10,
                 proxies: Optional[dict] = None):
        self._conn = HTTPClient(url, username, key, timeout, adapter, pool_size=pool_size, proxies=proxies)
        self._read_consistency = read_consistency

    @property
    def http_client(self):
        return self._conn

    def exists_db(self, database_name: str) -> bool:
        """Check if the database exists.

        Args:
            database_name (str): The name of the database to check.

        Returns:
            Bool: True if database exists else False.
        """
        for db in self.list_databases():
            if db.database_name == database_name:
                return True
        return False

    def create_database(self, database_name: str, timeout: Optional[float] = None) -> Database:
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
        db = Database(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        db.create_database(timeout=timeout)
        return db

    def create_database_if_not_exists(self, database_name: str, timeout: Optional[float] = None) -> Database:
        """Create the database if it doesn't exist.

        Args:
            database_name (str): The name of the database. A database name can only include
                numbers, letters, and underscores, and must not begin with a letter, and length
                must between 1 and 128
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Database: A database object.
        """
        for db in self.list_databases(timeout=timeout):
            if db.database_name == database_name:
                return db
        return self.create_database(database_name=database_name, timeout=timeout)

    def create_ai_database(self, database_name: str, timeout: Optional[float] = None) -> AIDatabase:
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
        db = AIDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        db.create_database(timeout=timeout)
        return db

    def drop_database(self, database_name: str, timeout: Optional[float] = None) -> Dict:
        """Delete a database.

        Args:
            database_name (str): The name of the database to delete.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        db = Database(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        return db.drop_database(timeout=timeout)

    def drop_ai_database(self, database_name: str, timeout: Optional[float] = None) -> Dict:
        """Delete an AI doc database.

        Args:
            database_name (str): The name of the database to delete.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        db = AIDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        return db.drop_database(timeout=timeout)

    def list_databases(self, timeout: Optional[float] = None) -> List[Union[AIDatabase, Database]]:
        """List all databases.

        Args:
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all AIDatabase and Database
        """
        db = Database(conn=self._conn, read_consistency=self._read_consistency)
        return db.list_databases(timeout=timeout)

    def database(self, database: str) -> Union[Database, AIDatabase]:
        """Get a database.

        Args:
            database (str): The name of the database.

        Returns:
            A Database or AIDatabase object
        """
        for db in self.list_databases():
            if db.database_name == database:
                return db
        raise exceptions.ParamError(message='Database not exist: {}'.format(database))

    def close(self):
        """Close the connection."""
        if self._conn:
            self._conn.close()

    def exists_collection(self,
                          database_name: str,
                          collection_name: str) -> bool:
        """Check if the collection exists.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection to check.

        Returns:
            Bool: True if collection exists else False.
        """
        return Database(conn=self._conn, name=database_name).exists_collection(collection_name)

    def upsert(self,
               database_name: str,
               collection_name: str,
               documents: List[Union[Document, Dict]],
               timeout: Optional[float] = None,
               build_index: bool = True,
               **kwargs):
        """Upsert documents into a collection.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            documents (List[Union[Document, Dict]]) : The list of the document object or dict to upsert. Maximum 1000.
            timeout (float) : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.
            build_index (bool) : An option for build index time when upsert, if build_index is true, will build index
                                 immediately, it will affect performance of upsert. And param buildIndex has same
                                 semantics with build_index, any of them false will be false

        Returns:
            Dict: Contains affectedCount
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).upsert(
            documents=documents,
            timeout=timeout,
            build_index=build_index,
            **kwargs
        )

    def delete(self,
               database_name: str,
               collection_name: str,
               document_ids: List[str] = None,
               filter: Union[Filter, str] = None,
               timeout: Optional[float] = None) -> Dict:
        """Delete document by conditions.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            document_ids (List[str]): The list of the document id
            filter (Union[Filter, str]): Filter condition of the scalar index field
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            Dict: Contains affectedCount
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).delete(
            document_ids=document_ids,
            filter=filter,
            timeout=timeout,
        )

    def update(self,
               database_name: str,
               collection_name: str,
               data: Union[Document, Dict],
               filter: Union[Filter, str] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None) -> Dict:
        """Update document by conditions.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            data (Union[Document, Dict]): Set the fields to be updated.
            document_ids (List[str]): The list of the document id
            filter (Union[Filter, str]): Filter condition of the scalar index field
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            Dict: Contains affectedCount
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).update(
            data=data,
            filter=filter,
            document_ids=document_ids,
            timeout=timeout,
        )

    def query(self,
              database_name: str,
              collection_name: str,
              document_ids: Optional[List] = None,
              retrieve_vector: bool = False,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              filter: Union[Filter, str] = None,
              output_fields: Optional[List[str]] = None,
              timeout: Optional[float] = None,
              ) -> List[Dict]:
        """Query documents that satisfies the condition.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            document_ids (List[str]): The list of the document id
            retrieve_vector (bool): Whether to return vector values
            limit (int): All ids of the document to be queried
            offset (int): Page offset, used to control the starting position of the results
            filter (Union[Filter, str]): Filter condition of the scalar index field
            output_fields (List[str]): document's fields to return
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            List[Dict]: all matched documents
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).query(
            document_ids=document_ids,
            retrieve_vector=retrieve_vector,
            limit=limit,
            offset=offset,
            filter=filter,
            output_fields=output_fields,
            timeout=timeout,
        )

    def search(self,
               database_name: str,
               collection_name: str,
               vectors: Union[List[List[float]], ndarray],
               filter: Union[Filter, str] = None,
               params=None,
               retrieve_vector: bool = False,
               limit: int = 10,
               output_fields: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ) -> List[List[Dict]]:
        """Search the most similar vector by the given vectors. Batch API

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            vectors (Union[List[List[float]], ndarray]): The list of vectors
            filter (Union[Filter, str]): Filter condition of the scalar index field
            params (SearchParams): query parameters
                FLAT: No parameters need to be specified.
                HNSW: ef, specifying the number of vectors to be accessed. Value range [1,32768], default is 10.
                IVF series: nprobe, specifying the number of units to be queried. Value range [1,nlist].
            retrieve_vector (bool): Whether to return vector values
            limit (int): All ids of the document to be queried
            output_fields (List[str]): document's fields to return
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            List[List[Dict]]: Return the most similar document for each vector.
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).search(
            vectors=vectors,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def search_by_id(self,
                     database_name: str,
                     collection_name: str,
                     document_ids: List[str],
                     filter: Union[Filter, str] = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     ) -> List[List[Dict]]:
        """Search the most similar vector by id. Batch API

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            document_ids (List[str]): The list of the document id
            filter (Union[Filter, str]): Filter condition of the scalar index field
            params (SearchParams): query parameters
                FLAT: No parameters need to be specified.
                HNSW: ef, specifying the number of vectors to be accessed. Value range [1,32768], default is 10.
                IVF series: nprobe, specifying the number of units to be queried. Value range [1,nlist].
            retrieve_vector (bool): Whether to return vector values
            limit (int): All ids of the document to be queried
            output_fields (List[str]): document's fields to return
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            List[List[Dict]]: Return the most similar document for each id.
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).searchById(
            document_ids=document_ids,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            timeout=timeout,
            output_fields=output_fields,
        )

    def search_by_text(self,
                       database_name: str,
                       collection_name: str,
                       embedding_items: List[str],
                       filter: Union[Filter, str] = None,
                       params=None,
                       retrieve_vector: bool = False,
                       limit: int = 10,
                       output_fields: Optional[List[str]] = None,
                       timeout: Optional[float] = None,
                       ) -> Dict[str, Any]:
        """Search the most similar vector by the embeddingItem. Batch API
        The embedding_items will first be embedded into a vector by the model set by the collection on the server side.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            embedding_items (Union[List[List[float]], ndarray]): The list of vectors
            filter (Union[Filter, str]): Filter condition of the scalar index field
            params (SearchParams): query parameters
                FLAT: No parameters need to be specified.
                HNSW: ef, specifying the number of vectors to be accessed. Value range [1,32768], default is 10.
                IVF series: nprobe, specifying the number of units to be queried. Value range [1,nlist].
            retrieve_vector (bool): Whether to return vector values
            limit (int): All ids of the document to be queried
            output_fields (List[str]): document's fields to return
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            List[List[Dict]]: Return the most similar document for each embedding_item.
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).searchByText(
            embeddingItems=embedding_items,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def hybrid_search(self,
                      database_name: str,
                      collection_name: str,
                      ann: Optional[Union[List[AnnSearch], AnnSearch]] = None,
                      match: Optional[Union[List[KeywordSearch], KeywordSearch]] = None,
                      filter: Union[Filter, str] = None,
                      rerank: Optional[Rerank] = None,
                      retrieve_vector: Optional[bool] = None,
                      output_fields: Optional[List[str]] = None,
                      limit: Optional[int] = None,
                      timeout: Optional[float] = None,
                      **kwargs) -> List[List[Dict]]:
        """Dense Vector and Sparse Vector Hybrid Retrieval

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            ann (Union[List[AnnSearch], AnnSearch]): Sparse vector search params
            match (Union[List[KeywordSearch], KeywordSearch): Ann params for search
            filter (Union[Filter, str]): Filter condition of the scalar index field
            rerank (Rerank): rerank params, RRFRerank, WeightedRerank
            retrieve_vector (bool): Whether to return vector values
            limit (int): All ids of the document to be queried
            output_fields (List[str]): document's fields to return
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            Union[List[List[Dict], [List[Dict]]: Return the most similar document for each condition.
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).hybrid_search(
            database_name=database_name,
            collection_name=collection_name,
            ann=ann,
            match=match,
            filter=filter,
            rerank=rerank,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            timeout=timeout,
            **kwargs)

    def add_index(self,
                  database_name: str,
                  collection_name: str,
                  indexes: List[FilterIndex],
                  build_existed_data: bool = True,
                  timeout: Optional[float] = None) -> dict:
        """Add scalar field index to existing collection.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection
            indexes (List[FilterIndex]): The scalar fields to add
            build_existed_data (bool): Whether scan historical Data and build index. Default is True.
                    If all fields are newly added, no need to scan historical data; can be set to False.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.

        Returns:
            dict: The API returns a code and msg. For example: {"code": 0,  "msg": "Operation success"}
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).add_index(indexes=indexes,
                    build_existed_data=build_existed_data,
                    timeout=timeout)
