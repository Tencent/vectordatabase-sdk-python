from typing import Dict, List, Optional, Any

from tcvectordb.model.collection import Collection
from tcvectordb.model.collection_view import Embedding
from tcvectordb.model.document import Document, Filter
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index
from tcvectordb.rpc.client.rpcclient import RPCClient
from tcvectordb.rpc.proto import olama_pb2


class RPCCollection(Collection):

    def __init__(self,
                 db,
                 name: str = '',
                 shard=0,
                 replicas=0,
                 description='',
                 index: Index = None,
                 embedding: Embedding = None,
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 rpc_client=None,
                 **kwargs):
        super().__init__(db,
                         name,
                         shard,
                         replicas,
                         description,
                         index,
                         embedding,
                         read_consistency,
                         **kwargs)
        self.rpc_client: RPCClient = rpc_client

    def upsert(self,
               documents: List[Document],
               timeout: Optional[float] = None,
               build_index: bool = True,
               **kwargs):
        buildIndex = bool(kwargs.get("buildIndex", True))
        res_build_index = buildIndex and build_index
        doc_list = []
        for doc in documents:
            doc_list.append(self._doc2pb(doc))
        request = olama_pb2.UpsertRequest(
            database=self.database_name,
            collection=self.collection_name,
            documents=doc_list,
            buildIndex=res_build_index,
        )
        result: olama_pb2.UpsertResponse = self.rpc_client.upsert(request, timeout=timeout)
        return {
            'code': result.code,
            'msg': result.msg,
            'affectedCount': result.affectedCount
        }

    def query(self,
              document_ids: Optional[List] = None,
              retrieve_vector: bool = False,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              filter: Optional[Filter] = None,
              output_fields: Optional[List[str]] = None,
              timeout: Optional[float] = None,
              ) -> List[Dict]:
        query = olama_pb2.QueryCond(
            retrieveVector=retrieve_vector,
        )
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter.cond
        if retrieve_vector is not None:
            query.retrieveVector = retrieve_vector
        if limit is not None:
            query.limit = limit
        if offset is not None:
            query.offset = offset
        if output_fields is not None:
            query.outputFields.extend(output_fields)
        request = olama_pb2.QueryRequest(
            database=self.database_name,
            collection=self.collection_name,
            query=query,
            readConsistency=self._read_consistency.value,
        )
        result: olama_pb2.QueryResponse = self.rpc_client.query(request, timeout=timeout)
        res = []
        for d in result.documents:
            res.append(self._pb2doc(d))
        return res

    def delete(self,
               document_ids: List[str] = None,
               filter: Filter = None,
               timeout: float = None,
               ):
        query = olama_pb2.QueryCond()
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter.cond
        request = olama_pb2.DeleteRequest(
            database=self.database_name,
            collection=self.collection_name,
            query=query,
        )
        result: olama_pb2.DeleteResponse = self.rpc_client.delete(request, timeout=timeout)
        return {
            'code': result.code,
            'msg': result.msg,
            'affectedCount': result.affectedCount
        }

    def update(self,
               data: Document,
               filter: Optional[Filter] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ):
        query = olama_pb2.QueryCond()
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter.cond
        request = olama_pb2.UpdateRequest(
            database=self.database_name,
            collection=self.collection_name,
            query=query,
            update=self._doc2pb(data),
        )
        result: olama_pb2.UpdateResponse = self.rpc_client.update(request, timeout=timeout)
        return {
            'warning': result.warning,
            'affectedCount': result.affectedCount
        }

    def search(self,
               vectors: List[List[float]],
               filter: Filter = None,
               params=None,
               retrieve_vector: bool = False,
               limit: int = 10,
               output_fields: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ) -> List[List[Dict]]:
        return self._base_search(
            vectors=vectors,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            timeout=timeout,
            output_fields=output_fields,
        ).get('documents')

    def searchById(self,
                   document_ids: List,
                   filter: Filter = None,
                   params=None,
                   retrieve_vector: bool = False,
                   limit: int = 10,
                   timeout: Optional[float] = None,
                   output_fields: Optional[List[str]] = None
    ) -> List[List[Dict]]:
        return self._base_search(
            document_ids=document_ids,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            timeout=timeout,
            output_fields=output_fields,
        ).get('documents')

    def searchByText(self,
                     embeddingItems: List[str],
                     filter: Filter = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     ) -> Dict[str, Any]:
        return self._base_search(
            embeddingItems=embeddingItems,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def _base_search(self,
                     vectors: List[List[float]] = None,
                     filter: Filter = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     document_ids: List[str] = None,
                     embeddingItems: List[str] = None,
                     ) -> Dict[str, Any]:
        search = olama_pb2.SearchCond()
        if vectors is not None:
            for v in vectors:
                search.vectors.append(olama_pb2.VectorArray(vector=v))
        if document_ids is not None:
            search.documentIds.extend(document_ids)
        if embeddingItems is not None:
            search.embeddingItems.extend(embeddingItems)
        if params is not None:
            if not isinstance(params, dict):
                params = vars(params)
            if params.get('ef') is not None:
                search.params.ef = params.get('ef')
            if params.get('nprobe') is not None:
                search.params.nprobe = params.get('nprobe')
            if params.get('radius') is not None:
                search.params.radius = params.get('radius')
        if filter is not None:
            search.filter = filter.cond
        if output_fields is not None:
            search.outputfields.extend(output_fields)
        if retrieve_vector is not None:
            search.retrieveVector = retrieve_vector
        if limit is not None:
            search.limit = limit
        request = olama_pb2.SearchRequest(
            database=self.database_name,
            collection=self.collection_name,
            readConsistency=self._read_consistency.value,
            search=search,
        )
        res: olama_pb2.SearchResponse = self.rpc_client.search(request, timeout=timeout)
        rtl = []
        for r in res.results:
            docs = []
            for d in r.documents:
                docs.append(self._pb2doc(d))
            rtl.append(docs)
        return {
            'warning': res.warning,
            'documents': rtl
        }

    def _pb2doc(self, d: olama_pb2.Document) -> dict:
        doc = {
            'id': d.id,
        }
        if d.score:
            doc['score'] = d.score
        if d.vector:
            vecs = []
            for v in d.vector:
                vecs.append(v.real)
            doc['vector'] = vecs
        for k, v in d.fields.items():
            if len(v.val_str) > 0:
                doc[k] = str(v.val_str, encoding='utf-8')
            elif len(v.val_str_arr.str_arr) > 0:
                arr = []
                for a in v.val_str_arr.str_arr:
                    arr.append(str(a, encoding='utf-8'))
                doc[k] = arr
            else:
                doc[k] = v.val_u64
        return doc

    def _doc2pb(self, doc: Document) -> olama_pb2.Document:
        doc_dict = vars(doc)
        d = olama_pb2.Document()
        if 'id' in doc_dict:
            d.id = doc_dict.pop('id')
        if 'vector' in doc_dict:
            d.vector.extend(doc_dict.pop('vector'))
        for k, v in doc_dict.items():
            if isinstance(v, int):
                d.fields[k].val_u64 = v
            elif isinstance(v, str):
                d.fields[k].val_str = bytes(v, encoding='utf-8')
            elif isinstance(v, list):
                al = []
                for arr in v:
                    al.append(bytes(arr, encoding='utf-8'))
                d.fields[k].val_str_arr.str_arr.extend(al)
            else:
                continue
        return d
