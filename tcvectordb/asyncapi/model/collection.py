from typing import Dict, List, Optional, Any, Union

from numpy import ndarray

from tcvectordb.model.collection import Collection, FilterIndexConfig
from tcvectordb.model.collection_view import Embedding
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index, SparseVector


class AsyncCollection(Collection):
    """AsyncCollection

    Contains Collection property and document API..

    Args:
        db (Database): Database object.
        name (str): collection name.
        shard (int): The shard number of the collection.
        replicas (int): The replicas number of the collection.
        description (str): An optional description of the collection.
        index (Index): A list of the index properties for the documents in a collection.
        read_consistency (ReadConsistency): STRONG_CONSISTENCY or EVENTUAL_CONSISTENCY for query
        embedding (Embedding): An optional embedding for embedding text when upsert documents.
        ttl_config (dict): TTL configuration, when set {'enable': True, 'timeField': 'expire_at'} means
            that ttl is enabled and automatically removed when the time set in the expire_at field expires
        filter_index_config (FilterIndexConfig): Enabling full indexing mode.
            Where all scalar fields are indexed by default.
        kwargs:
            create_time(str): collection create time
    """

    def __init__(self,
                 db,
                 name: str = '',
                 shard=0,
                 replicas=0,
                 description='',
                 index: Index = None,
                 embedding: Embedding = None,
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 ttl_config: dict = None,
                 filter_index_config: FilterIndexConfig = None,
                 **kwargs
                 ):
        super().__init__(db,
                         name,
                         shard,
                         replicas,
                         description,
                         index,
                         embedding,
                         read_consistency,
                         ttl_config=ttl_config,
                         filter_index_config=filter_index_config,
                         **kwargs)

    async def upsert(self,
                     documents: List[Union[Document, Dict]],
                     timeout: Optional[float] = None,
                     build_index: bool = True,
                     **kwargs):
        """Upsert documents into a collection.

        Args:
            documents (List[Union[Document, Dict]]) : The list of the document object or dict to upsert. Maximum 1000.
            timeout (float) : An optional duration of time in seconds to allow for the request.
                              When timeout is set to None, will use the connect timeout.
            build_index (bool) : An option for build index time when upsert, if build_index is true, will build index
                                 immediately, it will affect performance of upsert. And param buildIndex has same
                                 semantics with build_index, any of them false will be false

        Returns:
            Dict: Contains affectedCount
        """
        return super().upsert(documents,
                              timeout,
                              build_index,
                              **kwargs)

    async def query(self,
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
        return super().query(document_ids,
                             retrieve_vector,
                             limit,
                             offset,
                             filter,
                             output_fields,
                             timeout,
                             sort=sort)

    async def search(self,
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
        return super().search(vectors,
                              filter,
                              params,
                              retrieve_vector,
                              limit,
                              output_fields,
                              timeout,
                              radius=radius)

    async def searchById(self,
                         document_ids: List,
                         filter: Union[Filter, str] = None,
                         params=None,
                         retrieve_vector: bool = False,
                         limit: int = 10,
                         timeout: Optional[float] = None,
                         output_fields: Optional[List[str]] = None,
                         radius: Optional[float] = None,
                         ) -> List[List[Dict]]:
        """Search the most similar vector by id. Batch API

        Args:
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
        return super().searchById(document_ids,
                                  filter,
                                  params,
                                  retrieve_vector,
                                  limit,
                                  timeout,
                                  output_fields,
                                  radius=radius)

    async def searchByText(self,
                           embeddingItems: List[str],
                           filter: Union[Filter, str] = None,
                           params=None,
                           retrieve_vector: bool = False,
                           limit: int = 10,
                           output_fields: Optional[List[str]] = None,
                           timeout: Optional[float] = None,
                           radius: Optional[float] = None,
                           ) -> Dict[str, Any]:
        """Search the most similar vector by the embeddingItem. Batch API
        The embeddingItem will first be embedded into a vector by the model set by the collection on the server side.

        Args:
            embeddingItems (Union[List[List[float]], ndarray]): The list of vectors
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
            List[List[Dict]]: Return the most similar document for each embeddingItem.
        """
        return super().searchByText(embeddingItems,
                                    filter,
                                    params,
                                    retrieve_vector,
                                    limit,
                                    output_fields,
                                    timeout,
                                    radius=radius,)

    async def hybrid_search(self,
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
        return super().hybrid_search(
            ann=ann,
            match=match,
            filter=filter,
            rerank=rerank,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            timeout=timeout,
            **kwargs)

    async def fulltext_search(self,
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
        return super().fulltext_search(
            data=data,
            field_name=field_name,
            filter=filter,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            terminate_after=terminate_after,
            cutoff_frequency=cutoff_frequency,
            **kwargs)

    async def delete(self,
                     document_ids: List[str] = None,
                     filter: Union[Filter, str] = None,
                     timeout: float = None,
                     limit: Optional[int] = None) -> Dict:
        """Delete document by conditions.

        Args:
            document_ids (List[str]): The list of the document id
            filter (Union[Filter, str]): Filter condition of the scalar index field
            limit (int): The amount of document deleted, with a range of [1, 16384].
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            Dict: Contains affectedCount
        """
        return super().delete(document_ids, filter, timeout, limit=limit)

    async def update(self,
                     data: Union[Document, Dict],
                     filter: Union[Filter, str] = None,
                     document_ids: Optional[List[str]] = None,
                     timeout: Optional[float] = None) -> Dict:
        """Update document by conditions.

        Args:
            data (Union[Document, Dict]): Set the fields to be updated.
            document_ids (List[str]): The list of the document id
            filter (Union[Filter, str]): Filter condition of the scalar index field
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            Dict: Contains affectedCount
        """
        return super().update(data, filter, document_ids, timeout)

    async def rebuild_index(self,
                            drop_before_rebuild: bool = False,
                            throttle: Optional[int] = None,
                            timeout: Optional[float] = None,
                            field_name: Optional[str] = None):
        """Rebuild all indexes under the specified collection.

        Args:
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
        super().rebuild_index(drop_before_rebuild=drop_before_rebuild,
                              throttle=throttle,
                              timeout=timeout,
                              field_name=field_name)
