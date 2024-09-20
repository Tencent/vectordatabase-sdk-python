from typing import Dict, List, Optional, Any, Union

from tcvectordb.model.index import IndexField, VectorIndex, FilterIndex

from tcvectordb import exceptions
from .document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from .enum import EmbeddingModel, ReadConsistency
from .index import Index


class Embedding:
    """init Embedding"""

    def __init__(self, vector_field: str = None, status: str = 'disabled', field: str = None,
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


class BaseQuery:
    """
    Query, query conditions
    Args:
        filter(str): filter rows before return result
        document_ids(List): filter rows by id list
    """

    def __init__(self,
                 filter: Optional[Filter] = None,
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
            res["filter"] = self._filter.cond

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
    """

    def __init__(self,
                 limit: Optional[int] = None,
                 offset: Optional[int] = None,
                 retrieve_vector: bool = False,
                 filter: Optional[Filter] = None,
                 document_ids: Optional[List] = None,
                 output_fields: Optional[List[str]] = None
                 ):

        super().__init__(filter, document_ids)
        self._limit = limit
        self._offset = offset
        self._retrieve_vector = retrieve_vector

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
        res.update(super().__dict__)
        return res


class DeleteQuery(BaseQuery):
    def __init__(self,
                 filter: Optional[Filter] = None,
                 document_ids: Optional[List[str]] = None):
        super().__init__(filter, document_ids)

    @property
    def __dict__(self):
        return super().__dict__


class UpdateQuery(BaseQuery):
    def __init__(self,
                 filter: Optional[Filter] = None,
                 document_ids: Optional[List[str]] = None):
        super().__init__(filter, document_ids)

    @property
    def __dict__(self):
        return super().__dict__


class Search:
    def __init__(self,
                 retrieve_vector: bool = False,
                 limit: int = 10,
                 vectors: Optional[List[List[float]]] = None,
                 document_ids: Optional[List[str]] = None,
                 embedding_items: Optional[List[str]] = None,
                 params: Optional[Any] = None,
                 filter: Optional[Filter] = None,
                 output_fields: Optional[List[str]] = None
                 ):
        self._retrieve_vector = retrieve_vector
        self._limit = limit
        self.vectors = vectors
        if document_ids is not None:
            self._document_ids = document_ids

        self.embedding_items = embedding_items

        if params is not None:
            self._params = params

        if filter is not None and filter.cond:
            self._filter = filter

        if output_fields is not None:
            self._output_fields = output_fields

    @property
    def __dict__(self):
        res = {
            "retrieveVector": self._retrieve_vector,
            "limit": self._limit,
        }

        if self.vectors is not None:
            res["vectors"] = self.vectors

        if hasattr(self, "_document_ids"):
            res["documentIds"] = self._document_ids

        if self.embedding_items is not None:
            res["embeddingItems"] = self.embedding_items

        if hasattr(self, "_params"):
            res["params"] = vars(self._params)

        if hasattr(self, "_filter"):
            res["filter"] = vars(self._filter)

        if hasattr(self, "_output_fields"):
            res["outputFields"] = self._output_fields

        return res


class Collection():
    """
    Collection, about document operating.
    Args:
        db(Database): Database object.
        name(str): collection name.
        shard(int): The shard number of the collection.
        replicas(int): The replicas number of the collection.
        description(str): An optional description of the collection.
        index(Index): A list of the index properties for the documents in a collection.
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
        self.create_time = kwargs.pop('createTime', None)
        self.document_count = kwargs.pop("documentCount", None)
        self.alias = kwargs.pop("alias", None)
        self.index_status = kwargs.pop("indexStatus", None)
        self._read_consistency = read_consistency
        self.kwargs = kwargs

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
        return res_dict

    def upsert(
            self,
            documents: List[Union[Document, Dict]],
            timeout: Optional[float] = None,
            build_index: bool = True,
            **kwargs
    ):
        """Upsert a document.

        :param documents: The list of the document, document must match the indexes of the collection.
        :type  documents: list[Document]

        :param build_index: An option for build index time when upsert, if build_index is true, will build index
                            immediately, it will affect performance of upsert. And param buildIndex has same
                            semantics with build_index, any of them false will be false
        :type  build_index: bool

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :param buildIndex:  An option for build index time when upsert, if build_index is buildIndex, will build index
                            immediately, it will affect performance of upsert. And param build_index has same
                            semantics with build_index, any of them false will be false
        :type buildIndex: bool
        """
        buildIndex = bool(kwargs.get("buildIndex", True))
        res_build_index = buildIndex and build_index
        body = {
            'database': self.database_name,
            'collection': self.collection_name,
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

    def query(
            self,
            document_ids: Optional[List] = None,
            retrieve_vector: bool = False,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            filter: Optional[Filter] = None,
            output_fields: Optional[List[str]] = None,
            timeout: Optional[float] = None,
    ) -> List[Dict]:
        """Query document by document ids.

        :param document_ids: The list of the document id.
        :type  document_ids: list, the inner type depends on the index id field_type

        :param retrieve_vector: Whether to return vector values.
        :type retrieve_vector: bool

        :param limit: the limit of the query result, not support now
        :type: int

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return Documents, the list of the document
        :rtype: list[Dict]
        """
        query_param = Query(limit=limit, offset=offset, retrieve_vector=retrieve_vector, filter=filter,
                            document_ids=document_ids, output_fields=output_fields)
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
            'collection': self.collection_name,
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
            vectors: List[List[float]],
            filter: Filter = None,
            params=None,
            retrieve_vector: bool = False,
            limit: int = 10,
            output_fields: Optional[List[str]] = None,
            timeout: Optional[float] = None,
    ) -> List[List[Dict]]:
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
        search_param = Search(retrieve_vector=retrieve_vector, limit=limit, vectors=vectors, filter=filter,
                              params=params, output_fields=output_fields)
        return self.__base_search(search=search_param, read_consistency=self._read_consistency, timeout=timeout).get(
            'documents')

    def searchById(
            self,
            document_ids: List,
            filter: Filter = None,
            params=None,
            retrieve_vector: bool = False,
            limit: int = 10,
            timeout: Optional[float] = None,
            output_fields: Optional[List[str]] = None
    ) -> List[List[Dict]]:
        """Search document by document id list.

        :param document_ids: The list of the document id.
        :type  document_ids: list

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

        search_param = Search(retrieve_vector=retrieve_vector, limit=limit, document_ids=document_ids,
                              filter=filter, params=params, output_fields=output_fields)
        return self.__base_search(search=search_param, read_consistency=self._read_consistency, timeout=timeout).get(
            'documents')

    def searchByText(self,
                     embeddingItems: List[str],
                     filter: Filter = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     ) -> Dict[str, Any]:
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        search_param = Search(retrieve_vector=retrieve_vector, limit=limit, embedding_items=embeddingItems,
                              filter=filter, params=params, output_fields=output_fields)
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
            'collection': self.collection_name,
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
            if tmp:
                documents_res.append(tmp)
        return {
            'warning': warn_msg,
            'documents': documents_res
        }

    def hybrid_search(self,
                      ann: Optional[List[AnnSearch]] = None,
                      match: Optional[List[KeywordSearch]] = None,
                      filter: Optional[Filter] = None,
                      rerank: Optional[Rerank] = None,
                      retrieve_vector: Optional[bool] = None,
                      output_fields: Optional[List[str]] = None,
                      limit: Optional[int] = None,
                      timeout: Optional[float] = None,
                      **kwargs) -> List[List[Dict]]:
        """hybrid search

        :param match: ann params for search.
        :type match : List[KeywordSearch]

        :param ann: sparse vector search params.
        :type ann : List[AnnSearch]

        :param filter: The optional filter condition of the scalar index field.
        :type filter: Filter

        :param rerank: rerank params for search.
        :type rerank : Rerank

        :param output_fields: document's fields to return.
        :type output_fields: list[str]

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
            search['filter'] = vars(filter)
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
            'collection': self.collection_name,
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
            if tmp:
                documents_res.append(tmp)
        return documents_res

    def delete(
            self,
            document_ids: List[str] = None,
            filter: Filter = None,
            timeout: float = None,
    ):
        """Delete document by document id list.

        :param document_ids: The list of the document id.
        :type  document_ids: list

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
        """

        delete_query_param = DeleteQuery(document_ids=document_ids, filter=filter)
        return self.__base_delete(delete_query=delete_query_param, timeout=timeout)

    def __base_delete(
            self,
            delete_query: DeleteQuery,
            timeout: Optional[float] = None,
    ):
        """Delete document by document id list.

        :param delete_query: The list of the document id.
        :type  delete_query: list

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
        """

        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        # if delete_query is not None and not delete_query.valid():
        #     raise exceptions.ParamError(code=-1,
        #                                 message='base_query both field document_ids and filter are None')

        body = {
            "database": self.database_name,
            "collection": self.collection_name,
            "query": vars(delete_query)
        }
        res = self._conn.post('/document/delete', body, timeout)
        return res.data()

    def update(self,
               data: Union[Document, Dict],
               filter: Optional[Filter] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None):
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
            'collection': self.collection_name,
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
                      throttle: int = 0,
                      timeout: Optional[float] = None):
        if not self.database_name or not self.collection_name:
            raise exceptions.ParamError(message="database_name or collection_name is blank")

        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'dropBeforeRebuild': drop_before_rebuild,
            'throttle': throttle
        }
        self._conn.post('/index/rebuild', body, timeout)
