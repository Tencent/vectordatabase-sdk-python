from typing import Dict, List, Optional

from tcvectordb import exceptions
from .document import Document, Filter
from .index import Index


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
        **kwargs
    ):
        self._conn = db.conn
        self._database = db.database_name
        self._collection = name
        self.shard = shard
        self.replicas = replicas
        self.description = description
        self._index = index

        self.create_time = kwargs.get('create_time', '')

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
    def __dict__(self):
        return {
            'database': self.database_name,
            'collection': self.collection_name,
            'replicaNum': self.replicas,
            'shardNum': self.shard,
            'description': self.description,
            'indexes': self.index.list()
        }

    def upsert(
        self,
        documents: List[Document],
        timeout: Optional[float] = None,
    ):
        """Upsert a document.

        :param documents: The list of the document, document must match the indexes of the collection.
        :type  documents: list[Document]

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
        """
        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'buildIndex': True,
            'documents': []
        }
        for doc in documents:
            body['documents'].append(vars(doc))

        self._conn.post('/document/upsert', body, timeout)

    def query(
        self,
        document_ids: List,
        retrieve_vector: bool = False,
        limit: int = 1,
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
        if not isinstance(document_ids, list):
            raise exceptions.ParamError(
                code=-1, message='document_ids parameter must be set as list')
        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'query': {
                'documentIds': document_ids,
                'retrieveVector': retrieve_vector,
            }
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
        search = {
            'vectors': vectors,
            'retrieveVector': retrieve_vector,
            'limit': limit,
        }
        if filter and filter.cond:
            search['filter'] = filter.cond
        if params:
            search['params'] = vars(params)

        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'search': search
        }
        res = self._conn.post('/document/search', body, timeout)
        documents = res.body.get('documents', None)
        if not documents:
            return None
        res = []
        for arr in documents:
            tmp = []
            for elem in arr:
                tmp.append(elem)
            if tmp:
                res.append(tmp)
        return res

    def searchById(
        self,
        document_ids: List,
        filter: Filter = None,
        params=None,
        retrieve_vector: bool = False,
        limit: int = 10,
        timeout: Optional[float] = None,
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
        search = {
            'documentIds': document_ids,
            'filter': filter.cond if filter else '',
            'retrieveVector': retrieve_vector,
            'limit': limit,
        }
        if params:
            search['params'] = vars(params)

        body = {
            'database': self.database_name,
            'collection': self.collection_name,
            'search': search
        }
        res = self._conn.post('/document/search', body, timeout)
        documents = res.body.get('documents', None)
        if not documents:
            return None
        res = []
        for arr in documents:
            tmp = []
            for elem in arr:
                tmp.append(elem)
            if tmp:
                res.append(tmp)
        return res

    def delete(
        self,
        document_ids: List,
        timeout: Optional[float] = None,
    ):
        """Delete document by document id list.

        :param document_ids: The list of the document id.
        :type  document_ids: list

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
        """
        if not isinstance(document_ids, list):
            raise exceptions.ParamError(
                code=-1, message='document_ids parameter must be set as list')

        body = {
            "database": self.database_name,
            "collection": self.collection_name,
            "query": {
                'documentIds': document_ids
            }
        }
        self._conn.post('/document/delete', body, timeout)
