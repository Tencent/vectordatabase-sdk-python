from typing import List, Optional, Union, Dict, Any

from numpy import ndarray
from requests.adapters import HTTPAdapter

from tcvectordb.model.enum import ReadConsistency

from .httpclient import HTTPClient
from tcvectordb.model.database import Database
from tcvectordb import exceptions
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model import permission
from tcvectordb.model.collection import Collection, Embedding, FilterIndexConfig
from tcvectordb.model.collection_view import SplitterProcess, ParsingProcess, CollectionView
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from tcvectordb.model.index import FilterIndex, VectorIndex, Index, IndexField, SparseVector


class VectorDBClient:
    """Client for vector db.

    Connect with the database instance using HTTP.
    """

    def __init__(self, url=None, username='', key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10,
                 proxies: Optional[dict] = None,
                 password: Optional[str] = None):
        self._conn = HTTPClient(url, username, key, timeout, adapter, pool_size=pool_size,
                                proxies=proxies, password=password)
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
        raise exceptions.ParamError(code=14100, message='Database not exist: {}'.format(database))

    def close(self):
        """Close the connection."""
        if self._conn:
            self._conn.close()

    def create_collection(self,
                          database_name: str,
                          collection_name: str,
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
            database_name (str): The name of the database.
            collection_name (str): The name of the collection. A collection name can only include
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
        return Database(conn=self._conn, name=database_name).create_collection(
            name=collection_name,
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

    def create_collection_if_not_exists(self,
                                        database_name: str,
                                        collection_name: str,
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
            database_name (str): The name of the database.
            collection_name (str): The name of the collection. A collection name can only include
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
        return Database(conn=self._conn, name=database_name).create_collection_if_not_exists(
            name=collection_name,
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

    def describe_collection(self,
                            database_name: str,
                            collection_name: str,
                            timeout: Optional[float] = None) -> Collection:
        """Get a Collection by name.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            A Collection object.
        """
        return Database(conn=self._conn, name=database_name).describe_collection(name=collection_name,
                                                                                 timeout=timeout)

    def collection(self, database_name: str, collection_name: str) -> Collection:
        """Get a Collection by name.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.

        Returns:
            A Collection object
        """
        return self.describe_collection(database_name=database_name,
                                        collection_name=collection_name)

    def list_collections(self, database_name: str, timeout: Optional[float] = None) -> List[Collection]:
        """List all collections in the database.

        Args:
            database_name (str): The name of the database.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            List: all Collections
        """
        return Database(conn=self._conn, name=database_name).list_collections(timeout=timeout)

    def drop_collection(self,
                        database_name: str,
                        collection_name: str,
                        timeout: Optional[float] = None) -> Dict:
        """Delete a collection by name.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            timeout (float): An optional duration of time in seconds to allow for the request. When timeout
                is set to None, will use the connect timeout.

        Returns:
            Dict: Contains code、msg、affectedCount
        """
        return Database(conn=self._conn, name=database_name).drop_collection(name=collection_name,
                                                                             timeout=timeout)

    def truncate_collection(self,
                            database_name: str,
                            collection_name: str) -> Dict:
        """Clear all the data and indexes in the Collection.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.

        Returns:
            Dict: Contains affectedCount
        """
        return Database(conn=self._conn, name=database_name).truncate_collection(collection_name=collection_name)

    def set_alias(self,
                  database_name: str,
                  collection_name: str,
                  collection_alias: str) -> Dict:
        """Set alias for collection.

        Args:
            database_name (str): The name of the database.
            collection_name  : The name of the collection.
            collection_alias : alias name to set.
        Returns:
            Dict: Contains affectedCount
        """
        return Database(conn=self._conn, name=database_name).set_alias(collection_name=collection_name,
                                                                       collection_alias=collection_alias)

    def delete_alias(self, database_name: str, alias: str) -> Dict:
        """Delete alias by name.

        Args:
            database_name (str): The name of the database.
            alias  : alias name to delete.

        Returns:
            Dict: Contains affectedCount
        """
        return Database(conn=self._conn, name=database_name).delete_alias(alias=alias)

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
               timeout: Optional[float] = None,
               limit: Optional[int] = None) -> Dict:
        """Delete document by conditions.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            document_ids (List[str]): The list of the document id
            filter (Union[Filter, str]): Filter condition of the scalar index field
            limit (int): The amount of document deleted, with a range of [1, 16384].
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
            limit=limit,
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
              sort: Optional[dict] = None,
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
            sort: (dict): Set order by, like {'fieldName': 'age', 'direction': 'desc'}, default asc

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
            sort=sort,
        )

    def count(self,
              database_name: str,
              collection_name: str,
              filter: Union[Filter, str] = None,
              timeout: float = None
              ) -> int:
        """Calculate the number of documents based on the query conditions.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection.
            filter (Union[Filter, str]): The optional filter condition of the scalar index field.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.

        Returns:
            int: The number of documents based on the query conditions
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).count(filter=filter, timeout=timeout)

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
               radius: Optional[float] = None,
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
            radius (float): Based on the score threshold for similarity retrieval.
                            IP: return when score >= radius, value range (-∞, +∞).
                            COSINE: return when score >= radius, value range [-1, 1].
                            L2: return when score <= radius, value range [0, +∞).

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
            radius=radius,
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
                     radius: Optional[float] = None,
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
            radius (float): Based on the score threshold for similarity retrieval.
                            IP: return when score >= radius, value range (-∞, +∞).
                            COSINE: return when score >= radius, value range [-1, 1].
                            L2: return when score <= radius, value range [0, +∞).

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
            radius=radius,
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
                       radius: Optional[float] = None,
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
            radius (float): Based on the score threshold for similarity retrieval.
                            IP: return when score >= radius, value range (-∞, +∞).
                            COSINE: return when score >= radius, value range [-1, 1].
                            L2: return when score <= radius, value range [0, +∞).

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
            radius=radius,
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

    def fulltext_search(self,
                        database_name: str,
                        collection_name: str,
                        data: SparseVector,
                        field_name: str = 'sparse_vector',
                        filter: Union[Filter, str] = None,
                        retrieve_vector: Optional[bool] = None,
                        output_fields: Optional[List[str]] = None,
                        limit: Optional[int] = None,
                        terminate_after: Optional[int] = None,
                        cutoff_frequency: Optional[float] = None,
                        **kwargs) -> List[Dict]:
        """Sparse Vector retrieval

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection
            data (List[List[Union[int, float]]]): sparse vector to search.
            field_name (str): Sparse Vector field name, default: sparse_vector
            filter (Union[Filter, str]): The optional filter condition of the scalar index field.
            retrieve_vector (bool):  Whether to return vector values.
            output_fields (List[str]): document's fields to return.
            limit (int): return TopK=limit document.
            terminate_after(int): Set the upper limit for the number of retrievals.
                    This can effectively control the rate. For large datasets, the recommended empirical value is 4000.
            cutoff_frequency(float): Sets the upper limit for the frequency or occurrence count of high-frequency terms.
                    If the term frequency exceeds the value of cutoffFrequency, the keyword is ignored.

        Returns:
            [List[Dict]: the list of the matched document
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).fulltext_search(
            data=data,
            field_name=field_name,
            filter=filter,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            terminate_after=terminate_after,
            cutoff_frequency=cutoff_frequency,
            **kwargs)

    def rebuild_index(self,
                      database_name: str,
                      collection_name: str,
                      drop_before_rebuild: bool = False,
                      throttle: Optional[int] = None,
                      timeout: Optional[float] = None,
                      field_name: Optional[str] = None):
        """Rebuild all indexes under the specified collection.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection
            drop_before_rebuild (bool): Whether to delete the old index before rebuilding the new index. Default False.
                                        true: first delete the old index and then rebuild the index.
                                        false: after creating the new index, then delete the old index.
            throttle (int): Whether to limit the number of CPU cores for building an index on a single node.
                            0: no limit.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.
            field_name (str): Specify the fields for the reconstructed index.
                              One of vector or sparse_vector. Default vector.
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).rebuild_index(
            drop_before_rebuild=drop_before_rebuild,
            throttle=throttle,
            timeout=timeout,
            field_name=field_name,
        )

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

    def drop_index(self,
                   database_name: str,
                   collection_name: str,
                   field_names: List[str],
                   timeout: Optional[float] = None) -> dict:
        """Drop scalar field index from an existing collection.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection.
            field_names (List[str]): Field names to be dropped.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.

        Returns:
            dict: The API returns a code and msg. For example: {"code": 0,  "msg": "Operation success"}
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).drop_index(field_names=field_names,
                     timeout=timeout)

    def modify_vector_index(self,
                            database_name: str,
                            collection_name: str,
                            vector_indexes: List[VectorIndex],
                            rebuild_rules: Optional[dict] = None,
                            timeout: Optional[float] = None) -> dict:
        """Adjust vector index parameters.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection
            vector_indexes (List[FilterIndex]): The vector fields to adjust
            rebuild_rules (dict): Specified rebuild rules.
                    This interface will trigger a rebuild after adjusting the parameters.
                    For example: {"drop_before_rebuild": True , "throttle": 1}
                    drop_before_rebuild (bool): Whether to delete the old index before rebuilding the new index during
                              index reconstruction. True: Delete the old index before rebuilding the index.
                    throttle (int): Whether to limit the number of CPU cores for building the index on a single node.
                              0: No limit on CPU cores. 1: CPU core count is 1.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.

        Returns:
            dict: The API returns a code and msg. For example:
           {
             "code": 0,
             "msg": "Start rebuilding. You can use the '/collection/describe' API to follow the progress of rebuilding."
           }
        """
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).modify_vector_index(vector_indexes=vector_indexes,
                              rebuild_rules=rebuild_rules,
                              timeout=timeout)

    def create_user(self,
                    user: str,
                    password: str) -> dict:
        """Create a user.

        Args:
            user (str): The username to create.
            password (str): The password of user.

        Returns:
            dict: The API returns a code and msg. For example:
           {
             "code": 0,
             "msg": "operation success"
           }
        """
        return permission.create_user(conn=self._conn,
                                      user=user,
                                      password=password)

    def drop_user(self, user: str) -> dict:
        """Drop a user.

        Args:
            user (str): The username to create.

        Returns:
            dict: The API returns a code and msg. For example:
           {
             "code": 0,
             "msg": "operation success"
           }
        """
        return permission.drop_user(conn=self._conn, user=user)

    def describe_user(self, user: str) -> dict:
        """Get a user info.

        Args:
            user (str): Username to get.

        Returns:
            dict: User info contains privileges. For example:
           {
              "user": "test_user",
              "createTime": "2024-10-01 00:00:00",
              "privileges": [
                {
                  "resource": "db0.*",
                  "actions": ["read"]
                }
              ]
            }
        """
        return permission.describe_user(conn=self._conn, user=user)

    def user_list(self) -> List[dict]:
        """Get all users under the instance.

        Returns:
            dict: User info list. For example:
            [
              {
                "user": "test_user",
                "createTime": "2024-10-01 00:00:00",
                "privileges": [
                  {
                    "resource": "db0.*",
                    "actions": ["read"]
                  }
                ]
              }
           ]
        """
        return permission.user_list(conn=self._conn)

    def change_password(self,
                        user: str,
                        password: str) -> dict:
        """Change password for user.

        Args:
            user (str): The user to change password.
            password (str): New password of the user.

        Returns:
            dict: The API returns a code and msg. For example:
           {
             "code": 0,
             "msg": "operation success"
           }
        """
        return permission.change_password(conn=self._conn,
                                          user=user,
                                          password=password)

    def grant_to_user(self,
                      user: str,
                      privileges: Union[dict, List[dict]]) -> dict:
        """Grant permission for user.

        Args:
            user (str): The user to grant permission.
            privileges (str): The privileges to grant. For example:
            {
              "resource": "db0.*",
              "actions": ["read"]
            }

        Returns:
            dict: The API returns a code and msg. For example:
           {
             "code": 0,
             "msg": "operation success"
           }
        """
        return permission.grant_to_user(conn=self._conn,
                                        user=user,
                                        privileges=privileges)

    def revoke_from_user(self,
                         user: str,
                         privileges: Union[dict, List[dict]]) -> dict:
        """Revoke permission for user.

        Args:
            user (str): The user to revoke permission.
            privileges (str): The privilege to revoke. For example:
            {
              "resource": "db0.*",
              "actions": ["read"]
            }

        Returns:
            dict: The API returns a code and msg. For example:
           {
             "code": 0,
             "msg": "operation success"
           }
        """
        return permission.revoke_from_user(conn=self._conn,
                                           user=user,
                                           privileges=privileges)

    def upload_file(self,
                    database_name: str,
                    collection_name: str,
                    local_file_path: str,
                    file_name: Optional[str] = None,
                    splitter_process: Optional[SplitterProcess] = None,
                    parsing_process: Optional[ParsingProcess] = None,
                    embedding_model: Optional[str] = None,
                    field_mappings: Optional[Dict[str, str]] = None,
                    metadata: Optional[dict] = None,
                    ) -> dict:
        """Upload file to a Base Database.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection
            local_file_path (str): File path to load
            file_name (str): File name as DocumentSet
            splitter_process (SplitterProcess): Args for splitter process
            parsing_process (ParsingProcess): Document parsing parameters
            embedding_model (str): embedding model
            metadata (Dict): Extra properties to save
            field_mappings (Dict): Field mappings for Collection to save. filename must be a filter index
                For example: {"filename": "file_name", "text": "text", "imageList": "images"}

        Returns:
            dict
        """
        return CollectionView(
            db=AIDatabase(conn=self._conn, name=database_name),
            name=collection_name,
        ).upload_file(
            local_file_path=local_file_path,
            file_name=file_name,
            splitter_process=splitter_process,
            parsing_process=parsing_process,
            embedding_model=embedding_model,
            field_mappings=field_mappings,
            metadata=metadata,
        )

    def get_image_url(self,
                      database_name: str,
                      collection_name: str,
                      document_ids: List[str],
                      file_name: str) -> List[List[dict]]:
        """Get image urls for document.

        Args:
            database_name (str): The name of the database where the collection resides.
            collection_name (str): The name of the collection
            document_ids (List[str]): Document ids
            file_name (str): file name
        Returns:
            List[List[dict]]:
        """
        return CollectionView(
            db=AIDatabase(conn=self._conn, name=database_name),
            name=collection_name,
        ).get_image_url(
            document_ids=document_ids,
            file_name=file_name,
        )

    def query_file_details(self,
                           database_name: str,
                           collection_name: str,
                           file_names: List[str] = None,
                           filter: Union[Filter, str] = None,
                           output_fields: Optional[List[str]] = None,
                           limit: Optional[int] = None,
                           offset: Optional[int] = None,
                           ) -> List[Dict]:
        """Query documents that satisfies the condition.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            file_names (List[str]): The list of the filename
            filter (Union[Filter, str]): Filter condition of the scalar index field
            output_fields (List[str]): document's fields to return
            limit (int): All ids of the document to be queried
            offset (int): Page offset, used to control the starting position of the results

        Returns:
            List[Dict]: all matched documents
        """
        return CollectionView(
            db=AIDatabase(conn=self._conn, name=database_name),
            name=collection_name,
        ).query_file_details(
            database_name=database_name,
            collection_name=collection_name,
            file_names=file_names,
            filter=filter,
            output_fields=output_fields,
            limit=limit,
            offset=offset,
            read_consistency=self._read_consistency,
        )
