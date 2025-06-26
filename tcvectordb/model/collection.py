from typing import Dict, List, Optional, Any, Union

from numpy import ndarray

from tcvectordb.model.index import IndexField, VectorIndex, FilterIndex, SparseVector

from tcvectordb import exceptions
from .document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from .enum import EmbeddingModel, ReadConsistency
from .index import Index


class Embedding:
    """init Embedding"""

    def __init__(self, vector_field: str = None, status: str = 'enabled', field: str = None,
                 model: EmbeddingModel = None, model_name: str = None):
        """
        init Embedding when create embedding collection

        Args:
            vector_field (str): vector field name
            status (str): status of embedding, enable is available, disabled is unavailable, status is invalid when
                create collection
            field (str): field name of embedding content
            model (EmbeddingModel): [Deprecated] embedding model enum, this is a deprecated parameter, it will be
                instead of arg model_name, if model and model_name both are not None, model_name is used first.
            model_name (str): model_name specify embedding model wher upsert documents

        Examples:
            >>> Embedding(vector_field="vector", field="text", model=EmbeddingModel.BGE_BASE_ZH)
            >>> Embedding(vector_field="vector", field="text", model_name="bge-large-zh")
        """
        self._status = status

        if field is not None and vector_field is not None:
            self._field = field
            if model_name is not None:
                self._model = model_name
            elif model is not None:
                self._model = model.model_name
            self._vector_field = vector_field

    @property
    def __dict__(self):
        res = {"status": self._status}

        if hasattr(self, '_field') and hasattr(self, '_model'):
            res["field"] = self._field
            res["model"] = self._model
            res["vectorField"] = self._vector_field

        return res

    def set_fields(self, **kwargs):
        self._field = kwargs.get("field")
        self._model = kwargs.get("model")
        self._vector_field = kwargs.get("vectorField")
        self._status = kwargs.get("status")


class FilterIndexConfig:
    """Enabling full indexing mode.
    Where all scalar fields are indexed by default. Disabled by default.
    """

    def __init__(self,
                 filter_all: Optional[bool] = None,
                 fields_without_index: Optional[List[str]] = None,
                 max_str_len: Optional[int] = None,
                 **kwargs,
                 ):
        """
        init FilterIndexConfig when create a collection

        Args:
            filter_all (bool): enable (true) and disable (false) control for full indexing mode.
            fields_without_index (list[str]): specify certain scalar fields not to create an index.
            max_str_len (int): The maximum length limit for the string field "value" is specified.
                               If more than, it will be truncated to the specified max_str_len value before indexing.
                               The default value is 32, and the valid range is between 1 and 65536.

        Examples:
            >>> FilterIndexConfig(filter_all=True, fields_without_index=['fieldName1'], max_str_len=32)
        """
        self.filter_all: Optional[bool] = filter_all
        self.fields_without_index: Optional[List[str]] = fields_without_index
        self.max_str_len: Optional[int] = max_str_len
        self._init(**kwargs)
        self.kwargs = kwargs

    def _init(self, **kwargs):
        if self.filter_all is None:
            self.filter_all = kwargs.pop('filterAll', None)
        if self.fields_without_index is None:
            self.fields_without_index = kwargs.pop('fieldsWithoutIndex', None)
        if self.max_str_len is None:
            self.max_str_len = kwargs.pop('maxStrLen', None)

    @property
    def __dict__(self):
        res = {}
        if self.filter_all is not None:
            res['filterAll'] = self.filter_all
        if self.fields_without_index is not None:
            res['fieldsWithoutIndex'] = self.fields_without_index
        if self.max_str_len is not None:
            res['maxStrLen'] = self.max_str_len
        res.update(self.kwargs)
        return res


class BaseQuery:
    """
    Query, query conditions
    Args:
        filter(str): filter rows before return result
        document_ids(List): filter rows by id list
    """

    def __init__(self,
                 filter: Union[Filter, str] = None,
                 document_ids: Optional[List[str]] = None
                 ):
        if filter is not None:
            self._filter = filter

        if document_ids is not None and len(document_ids) > 0:
            self._document_ids = document_ids

    @property
    def __dict__(self):
        res = {}

        if hasattr(self, "_filter"):
            res["filter"] = self._filter if isinstance(self._filter, str) else self._filter.cond

        if hasattr(self, "_document_ids"):
            res["documentIds"] = self._document_ids

        return res

    def valid(self) -> bool:
        if not hasattr(self, "_filter") and not hasattr(self, "_document_ids"):
            return False

        if hasattr(self, "_document_ids") and not isinstance(self._document_ids, list):
            return False

        return True


class Query(BaseQuery):
    """
    Query, query conditions
    Args:
        limit(int): Limit return row's count
        offset(int): Skip offset rows of query result set
        retrieve_vector(bool): Whether to return vector values.
        filter(Filter): filter rows before return result
        document_ids(List): filter rows by id list
        output_fields(List): return columns by column name list
        sort: (dict): Set order by, like {'fieldName': 'age', 'direction': 'desc'}, default asc
    """

    def __init__(self,
                 limit: Optional[int] = None,
                 offset: Optional[int] = None,
                 retrieve_vector: bool = False,
                 filter: Union[Filter, str] = None,
                 document_ids: Optional[List] = None,
                 output_fields: Optional[List[str]] = None,
                 sort: Optional[Union[List[dict], dict]] = None,
                 ):

        super().__init__(filter, document_ids)
        self._limit = limit
        self._offset = offset
        self._retrieve_vector = retrieve_vector
        self.sort = sort
        if self.sort is not None and not isinstance(self.sort, list):
            self.sort = [self.sort]
        if output_fields is not None and len(output_fields) > 0:
            self._output_fields = output_fields

    @property
    def __dict__(self):
        res = {
            "retrieveVector": self._retrieve_vector,
        }
        if self._limit is not None:
            res["limit"] = self._limit
        if self._offset is not None:
            res["offset"] = self._offset
        if hasattr(self, "_output_fields"):
            res["outputFields"] = self._output_fields
        if self.sort is not None:
            for s in self.sort:
                if s.get('direction') == '':
                    del s['direction']
            res['sort'] = self.sort
        res.update(super().__dict__)
        return res


class DeleteQuery(BaseQuery):
    def __init__(self,
                 filter: Union[Filter, str] = None,
                 document_ids: Optional[List[str]] = None,
                 limit: Optional[int] = None):
        super().__init__(filter, document_ids)
        self.limit = limit

    @property
    def __dict__(self):
        res = {}
        if self.limit is not None:
            res['limit'] = self.limit
        res.update(super().__dict__)
        return res


class UpdateQuery(BaseQuery):
    def __init__(self,
                 filter: Union[Filter, str] = None,
                 document_ids: Optional[List[str]] = None):
        super().__init__(filter, document_ids)

    @property
    def __dict__(self):
        return super().__dict__


class Search:
    def __init__(self,
                 retrieve_vector: bool = False,
                 limit: int = 10,
                 vectors: Union[List[List[float]], ndarray] = None,
                 document_ids: Optional[List[str]] = None,
                 embedding_items: Optional[List[str]] = None,
                 params: Optional[Any] = None,
                 filter: Union[Filter, str] = None,
                 output_fields: Optional[List[str]] = None,
                 radius: Optional[float] = None,
                 ):
        self._retrieve_vector = retrieve_vector
        self._limit = limit
        self.vectors = vectors
        if document_ids is not None:
            self._document_ids = document_ids

        self.embedding_items = embedding_items

        if params is not None:
            self._params = params

        if filter:
            if isinstance(filter, Filter):
                if filter.cond:
                    self._filter = filter
            else:
                self._filter = filter

        if output_fields is not None:
            self._output_fields = output_fields
        self.radius = radius

    @property
    def __dict__(self):
        res = {
            "retrieveVector": self._retrieve_vector,
            "limit": self._limit,
        }

        if self.vectors is not None:
            res["vectors"] = self.vectors.tolist() if isinstance(self.vectors, ndarray) else self.vectors

        if hasattr(self, "_document_ids"):
            res["documentIds"] = self._document_ids

        if self.embedding_items is not None:
            res["embeddingItems"] = self.embedding_items

        if hasattr(self, "_params"):
            res["params"] = vars(self._params)

        if hasattr(self, "_filter"):
            res["filter"] = self._filter if isinstance(self._filter, str) else self._filter.cond

        if hasattr(self, "_output_fields"):
            res["outputFields"] = self._output_fields

        if self.radius is not None:
            res['radius'] = self.radius

        return res


class Collection():
    """Collection

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

    def __init__(
            self,
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
        self._conn = db.conn
        self._database = db.database_name
        self._collection = name
        self.shard = shard
        self.replicas = replicas
        self.description = description
        self._embedding = embedding
        self._index = index
        self.ttl_config = ttl_config
        self.filter_index_config = filter_index_config
        self.create_time = kwargs.pop('createTime', None)
        self.document_count = kwargs.pop("documentCount", None)
        self.alias = kwargs.pop("alias", None)
        self.index_status = kwargs.pop("indexStatus", None)
        self._read_consistency = read_consistency
        self.kwargs = kwargs
        self.conn_name = name

    @property
    def database_name(self):
        return self._database

    @property
    def collection_name(self):
        return self._collection

    @property
    def index(self):
        return self._index

    @property
    def indexes(self) -> List[Union[IndexField, VectorIndex, FilterIndex]]:
        return list(self.index.indexes.values())

    @property
    def embedding(self):
        return self._embedding

    @property
    def __dict__(self):
        res_dict = {
            'database': self.database_name,
            'collection': self.collection_name,
            'replicaNum': self.replicas,
            'shardNum': self.shard,
            'indexes': self.index.list(),
        }
        if self._embedding is not None:
            res_dict['embedding'] = vars(self._embedding)
        if self.description:
            res_dict['description'] = self.description
        if self.create_time is not None:
            res_dict['createTime'] = self.create_time
        if self.document_count is not None:
            res_dict['documentCount'] = self.document_count
        if self.alias is not None:
            res_dict['alias'] = self.alias
        if self.index_status is not None:
            res_dict['indexStatus'] = self.index_status
        if self.ttl_config is not None:
            res_dict['ttlConfig'] = self.ttl_config
        if self.filter_index_config is not None:
            res_dict['filterIndexConfig'] = vars(self.filter_index_config)
        res_dict.update(self.kwargs)
        return res_dict

    def upsert(self,
               documents: List[Union[Document, Dict]],
               timeout: Optional[float] = None,
               build_index: bool = True,
               **kwargs) -> Dict:
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
        buildIndex = bool(kwargs.get("buildIndex", True))
        res_build_index = buildIndex and build_index
        body = {
            'database': self.database_name,
            'collection': self.conn_name,
            'buildIndex': res_build_index,
            'documents': []
        }
        ai = False
        if len(documents) > 0:
            if isinstance(documents[0], dict):
                ai = isinstance(documents[0].get('vector'), str)
            else:
                ai = isinstance(vars(documents[0]).get('vector'), str)
        for doc in documents:
            if isinstance(doc, dict):
                body['documents'].append(doc)
            else:
                body['documents'].append(vars(doc))
        res = self._conn.post('/document/upsert', body, timeout, ai=ai)
        return res.data()

    def query(self,
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
        query_param = Query(limit=limit, offset=offset, retrieve_vector=retrieve_vector, filter=filter,
                            document_ids=document_ids, output_fields=output_fields, sort=sort)
        return self.__base_query(query=query_param, read_consistency=self._read_consistency, timeout=timeout)

    def __base_query(self,
                     query: Query,
                     read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                     timeout: Optional[float] = None) -> List[Dict]:
        if query is None:
            raise exceptions.ParamError(
                code=-1, message='query is a required parameter')

        body = {
            'database': self.database_name,
            'collection': self.conn_name,
            'query': vars(query),
            'readConsistency': read_consistency.value
        }

        res = self._conn.post('/document/query', body, timeout)
        documents = res.body.get('documents', None)
        res = []
        if not documents:
            return []
        for doc in documents:
            res.append(doc)
        return res

    def search(
            self,
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
        search_param = Search(retrieve_vector=retrieve_vector, limit=limit, vectors=vectors, filter=filter,
                              params=params, output_fields=output_fields, radius=radius)
        return self.__base_search(search=search_param, read_consistency=self._read_consistency, timeout=timeout).get(
            'documents')

    def searchById(
            self,
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
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        search_param = Search(retrieve_vector=retrieve_vector, limit=limit, document_ids=document_ids,
                              filter=filter, params=params, output_fields=output_fields, radius=radius)
        return self.__base_search(search=search_param, read_consistency=self._read_consistency, timeout=timeout).get(
            'documents')

    def searchByText(self,
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
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        search_param = Search(retrieve_vector=retrieve_vector, limit=limit, embedding_items=embeddingItems,
                              filter=filter, params=params, output_fields=output_fields, radius=radius)
        return self.__base_search(search=search_param, read_consistency=self._read_consistency, timeout=timeout)

    def __base_search(
            self,
            search: Search,
            read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
            timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Search document by vector list.

        :param vectors: The list of the vector array.
        :type  vectors: list

        :param filter: The optional filter condition of the scalar index field.
        :type filter: Filter

        :param params: The params by searching. Currently, only HNSW collection vector type are supported.
        :type params: HNSWSearchParams, if collection vector type is hnsw.

        :param retrieve_vector: Whether to return vector values.
        :type retrieve_vector: bool

        :param limit: the limit of the query result, not support now
        :type: int

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return Documents, the list of the document
        :rtype: List[List[Dict]]
        """

        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        if search is None:
            raise exceptions.ParamError(message="search is None")

        body = {
            'database': self.database_name,
            'collection': self.conn_name,
            'readConsistency': read_consistency.value,
            'search': vars(search)
        }
        ai = False
        if isinstance(search.vectors, list) and \
                len(search.vectors) > 0 and isinstance(search.vectors[0], str):
            ai = True
        res = self._conn.post('/document/search', body, timeout, ai=ai)

        warn_msg = ""
        if res.body.get("warning", None) is not None and len(res.body.get("warning", None)) > 0:
            warn_msg = res.body.get("warning")

        documents = res.body.get('documents', None)

        if not documents:
            return {
                'warning': warn_msg,
                'documents': []
            }

        documents_res = []
        for arr in documents:
            tmp = []
            for elem in arr:
                tmp.append(elem)
            documents_res.append(tmp)
        return {
            'warning': warn_msg,
            'documents': documents_res
        }

    def hybrid_search(self,
                      ann: Optional[Union[List[AnnSearch], AnnSearch]] = None,
                      match: Optional[Union[List[KeywordSearch], KeywordSearch]] = None,
                      filter: Union[Filter, str] = None,
                      rerank: Optional[Rerank] = None,
                      retrieve_vector: Optional[bool] = None,
                      output_fields: Optional[List[str]] = None,
                      limit: Optional[int] = None,
                      timeout: Optional[float] = None,
                      **kwargs) -> List[Union[List[Dict], Dict]]:
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
        single = True
        if ann:
            if isinstance(ann, List):
                single = False
            else:
                ann = [ann]
        if match:
            if isinstance(match, List):
                single = False
            else:
                match = [match]
        search = {}
        ai = False
        if ann:
            search['ann'] = []
            for a in ann:
                search['ann'].append(vars(a))
            if len(ann) > 0 and ann[0].data is not None:
                if isinstance(ann[0].data, str):
                    ai = True
                elif len(ann[0].data) > 0 and isinstance(ann[0].data[0], str):
                    ai = True
        if match:
            search['match'] = []
            for m in match:
                search['match'].append(vars(m))
        if filter:
            search['filter'] = filter if isinstance(filter, str) else filter.cond
        if rerank:
            # if rerank.method == "wordsEmbedding":
            #     ai = True
            search['rerank'] = vars(rerank)
        if retrieve_vector is not None:
            search['retrieveVector'] = retrieve_vector
        if output_fields:
            search['outputFields'] = output_fields
        if limit is not None:
            search['limit'] = limit
        search.update(kwargs)
        body = {
            'database': self.database_name,
            'collection': self.conn_name,
            'readConsistency': self._read_consistency.value,
            'search': search,
        }
        res = self._conn.post('/document/hybridSearch', body, timeout, ai=ai)
        if 'warning' in res.body:
            Warning(res.body.get('warning'))
        documents = res.body.get('documents', None)
        if not documents:
            return []
        documents_res = []
        for arr in documents:
            tmp = []
            for elem in arr:
                tmp.append(elem)
            documents_res.append(tmp)
        if single:
            documents_res = documents_res[0]
        return documents_res

    def fulltext_search(self,
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
        match = {
            "fieldName": field_name,
            "data": [data],
        }
        if terminate_after is not None:
            match['terminateAfter'] = terminate_after
        if cutoff_frequency is not None:
            match['cutoffFrequency'] = cutoff_frequency
        search = {
            'match': match
        }
        if filter:
            search['filter'] = filter if isinstance(filter, str) else filter.cond
        if retrieve_vector is not None:
            search['retrieveVector'] = retrieve_vector
        if output_fields:
            search['outputFields'] = output_fields
        if limit is not None:
            search['limit'] = limit
        search.update(kwargs)
        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'readConsistency': self._read_consistency.value,
            'search': search,
        }
        res = self._conn.post('/document/fullTextSearch', body)
        if 'warning' in res.body:
            Warning(res.body.get('warning'))
        documents = res.body.get('documents', None)
        if not documents:
            return []
        documents_res = []
        for arr in documents:
            tmp = []
            for elem in arr:
                tmp.append(elem)
            documents_res.append(tmp)
        return documents_res[0]

    def delete(self,
               document_ids: List[str] = None,
               filter: Union[Filter, str] = None,
               timeout: float = None,
               limit: Optional[int] = None
               ) -> Dict:
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
        delete_query_param = DeleteQuery(document_ids=document_ids, filter=filter, limit=limit)
        return self.__base_delete(delete_query=delete_query_param, timeout=timeout)

    def __base_delete(
            self,
            delete_query: DeleteQuery,
            timeout: Optional[float] = None) -> Dict:
        """Delete document by conditions.

        Args:
            delete_query (DeleteQuery): Query conditions
            filter (Union[Filter, str]): Filter condition of the scalar index field
            timeout (float): An optional duration of time in seconds to allow for the request.
                             When timeout is set to None, will use the connect timeout.

        Returns:
            Dict: Contains affectedCount
        """
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")
        body = {
            "database": self.database_name,
            "collection": self.conn_name,
            "query": vars(delete_query)
        }
        res = self._conn.post('/document/delete', body, timeout)
        return res.data()

    def count(self,
              filter: Union[Filter, str] = None,
              timeout: float = None
              ) -> int:
        """Calculate the number of documents based on the query conditions.

        Args:
            filter (Union[Filter, str]): The optional filter condition of the scalar index field.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.

        Returns:
            int: The number of documents based on the query conditions
        """
        body = {
            "database": self.database_name,
            "collection": self.conn_name,
        }
        if self._read_consistency is not None:
            body['readConsistency'] = self._read_consistency.value
        query = {}
        if filter is not None:
            query['filter'] = filter if isinstance(filter, str) else filter.cond
        body['query'] = query
        res = self._conn.post('/document/count', body, timeout)
        return res.data().get('count')

    def update(self,
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
        if data is None:
            raise exceptions.ParamError(code=-1, message='data is None')

        update_query = UpdateQuery(document_ids=document_ids, filter=filter)
        return self.__base_update(update_query=update_query, document=data, timeout=timeout)

    def __base_update(self,
                      update_query: UpdateQuery,
                      document: Union[Document, Dict],
                      timeout: Optional[float] = None) -> Dict:
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        if update_query is None or not update_query.valid():
            raise exceptions.ParamError(code=-1, message='query both field document_ids and filter are None')

        if document is None:
            raise exceptions.ParamError(code=-1, message='document is None')
        body = {
            'database': self.database_name,
            'collection': self.conn_name,
            'query': vars(update_query)
        }
        ai = False
        if isinstance(document, dict):
            ai = isinstance(document.get('vector'), str)
        else:
            ai = isinstance(vars(document).get('vector'), str)
        body["update"] = document if isinstance(document, dict) else vars(document)
        postRes = self._conn.post('/document/update', body, timeout, ai=ai)
        resBody = postRes.body
        res = {}

        if 'warning' in resBody:
            res['warning'] = resBody.get("warning")

        if 'affectedCount' in resBody:
            res['affectedCount'] = resBody.get('affectedCount')

        return res

    def rebuild_index(self,
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
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'dropBeforeRebuild': drop_before_rebuild,
        }
        if throttle is not None:
            body['throttle'] = throttle
        if field_name is not None:
            body['fieldName'] = field_name
        self._conn.post('/index/rebuild', body, timeout)

    def add_index(self,
                  indexes: List[FilterIndex],
                  build_existed_data: bool = True,
                  timeout: Optional[float] = None) -> dict:
        """Add scalar field index to existing collection.

        Args:
            indexes (List[FilterIndex]): The scalar fields to add
            build_existed_data (bool): Whether scan historical Data and build index. Default is True.
                    If all fields are newly added, no need to scan historical data; can be set to False.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.

        Returns:
            dict: The API returns a code and msg. For example: {"code": 0,  "msg": "Operation success"}
        """
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")
        indexes = [vars(item) for item in indexes]
        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'indexes': indexes,
        }
        if build_existed_data is not None:
            body['buildExistedData'] = build_existed_data
        res = self._conn.post('/index/add', body, timeout)
        return res.data()

    def drop_index(self,
                   field_names: List[str],
                   timeout: Optional[float] = None) -> dict:
        """Drop scalar field index from an existing collection.

        Args:
            field_names (List[str]): Field names to be dropped.
            timeout (float): An optional duration of time in seconds to allow for the request.
                    When timeout is set to None, will use the connect timeout.

        Returns:
            dict: The API returns a code and msg. For example: {"code": 0,  "msg": "Operation success"}
        """
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")
        if not isinstance(field_names, list):
            raise exceptions.ParamError(message='Invalid value for List[str] field: field_names')
        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'fieldNames': field_names,
        }
        res = self._conn.post('/index/drop', body, timeout)
        return res.data()

    def modify_vector_index(self,
                            vector_indexes: List[VectorIndex],
                            rebuild_rules: Optional[dict] = None,
                            timeout: Optional[float] = None) -> dict:
        """Adjust vector index parameters.

        Args:
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
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")
        indexes = []
        for item in vector_indexes:
            index = vars(item)
            if hasattr(item, 'field_type_none') and item.field_type_none:
                del index['fieldType']
            indexes.append(index)
        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'vectorIndexes': indexes,
        }
        if rebuild_rules is not None:
            if 'drop_before_rebuild' in rebuild_rules:
                rebuild_rules['dropBeforeRebuild'] = rebuild_rules.pop('drop_before_rebuild')
            body['rebuildRules'] = rebuild_rules
        res = self._conn.post('/index/modifyVectorIndex', body, timeout)
        return res.data()
