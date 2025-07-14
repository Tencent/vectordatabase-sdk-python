import math
import time
from typing import List, Union, Dict, Optional, Any

import ujson
from numpy import ndarray
from tcvectordb.exceptions import ServerInternalError, ParamError, GrpcException
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.collection import Embedding, FilterIndexConfig
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank, WeightedRerank, RRFRerank
from tcvectordb.model.enum import ReadConsistency, FieldType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, SparseIndex, SparseVector, IndexField
from tcvectordb.rpc.client.rpcclient import RPCClient
from tcvectordb.rpc.model.collection import RPCCollection
from tcvectordb.rpc.model.database import RPCDatabase
from tcvectordb.rpc.proto import olama_pb2


class VdbClient:
    """VectorDB API wrapper use RPCClient"""

    def __init__(self,
                 client: RPCClient,
                 read_consistency: ReadConsistency,
                 ):
        self.rpc_client = client
        self.read_consistency = read_consistency
        self._split_cache = {}

    def close(self):
        self.rpc_client.close()

    def upsert(self,
               database_name: str,
               collection_name: str,
               documents: List[Union[Document, Dict]],
               timeout: Optional[float] = None,
               build_index: bool = True,
               **kwargs):
        buildIndex = bool(kwargs.get("buildIndex", True))
        res_build_index = buildIndex and build_index
        doc_list = []
        ai = False
        if len(documents) > 0:
            if isinstance(documents[0], dict):
                ai = isinstance(documents[0].get('vector'), str)
            else:
                ai = isinstance(vars(documents[0]).get('vector'), str)
        for doc in documents:
            doc_list.append(self._doc2pb(doc))
        request = olama_pb2.UpsertRequest(
            database=database_name,
            collection=collection_name,
            documents=doc_list,
            buildIndex=res_build_index,
        )
        result: olama_pb2.UpsertResponse = self.rpc_client.upsert(request, timeout=timeout, ai=ai)
        res = {
            'code': result.code,
            'msg': result.msg,
            'affectedCount': result.affectedCount
        }
        if result.embedding_extra_info and result.embedding_extra_info.token_used:
            res['embeddingExtraInfo'] = {'tokenUsed': result.embedding_extra_info.token_used}
        return res

    def delete(self,
               database_name: str,
               collection_name: str,
               document_ids: List[str] = None,
               filter: Union[Filter, str] = None,
               timeout: float = None,
               limit: Optional[int] = None):
        query = olama_pb2.QueryCond()
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter if isinstance(filter, str) else filter.cond
        if limit is not None:
            if limit == 0:
                raise ServerInternalError(code=15000,
                                          message=f'The value of limit cannot be 0.')
            query.limit = limit
        request = olama_pb2.DeleteRequest(
            database=database_name,
            collection=collection_name,
            query=query,
        )
        result: olama_pb2.DeleteResponse = self.rpc_client.delete(request, timeout=timeout)
        return {
            'code': result.code,
            'msg': result.msg,
            'affectedCount': result.affectedCount
        }

    def update(self,
               database_name: str,
               collection_name: str,
               data: Union[Document, Dict],
               filter: Union[Filter, str] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None):
        query = olama_pb2.QueryCond()
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter if isinstance(filter, str) else filter.cond
        ai = False
        if isinstance(data, dict):
            ai = isinstance(data.get('vector'), str)
        else:
            ai = isinstance(vars(data).get('vector'), str)
        request = olama_pb2.UpdateRequest(
            database=database_name,
            collection=collection_name,
            query=query,
            update=self._doc2pb(data),
        )
        result: olama_pb2.UpdateResponse = self.rpc_client.update(request, timeout=timeout, ai=ai)
        res = {
            'warning': result.warning,
            'affectedCount': result.affectedCount
        }
        if result.embedding_extra_info and result.embedding_extra_info.token_used:
            res['embeddingExtraInfo'] = {'tokenUsed': result.embedding_extra_info.token_used}
        return res

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
              sort: Optional[dict] = None) -> List[Dict]:
        query = olama_pb2.QueryCond(
            retrieveVector=retrieve_vector,
        )
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter if isinstance(filter, str) else filter.cond
        if retrieve_vector is not None:
            query.retrieveVector = retrieve_vector
        if limit is not None:
            if limit == 0:
                raise ServerInternalError(code=15000,
                                          message=f'The value of limit cannot be 0.')
            query.limit = limit
        if offset is not None:
            query.offset = offset
        if output_fields is not None:
            query.outputFields.extend(output_fields)
        if sort is not None:
            if not isinstance(sort, list):
                sort = [sort]
            for s in sort:
                direction = s.get('direction', '')
                if direction not in ('', 'asc', 'desc'):
                    raise ServerInternalError(code=15000,
                                              message='the sort rule direction must be asc or desc if input')
                desc = direction == 'desc'
                query.sort.append(olama_pb2.OrderRule(
                    fieldName=s.get('fieldName', ''),
                    desc=desc,
                ))
        request = olama_pb2.QueryRequest(
            database=database_name,
            collection=collection_name,
            query=query,
            readConsistency=self.read_consistency.value,
        )
        # result: olama_pb2.QueryResponse = self.rpc_client.query(request, timeout=timeout)
        result: Optional[olama_pb2.QueryResponse] = None
        key = f'query/{database_name}/{collection_name}/{retrieve_vector}'
        split_size = self._split_cache.get(key, 16385*2)
        if limit >= split_size:
            result = self._query_batch(request, key=key, timeout=timeout, suggest_limit=math.ceil(split_size / 2))
        else:
            try:
                result = self.rpc_client.query(request, timeout=timeout)
            except GrpcException as e:
                if "Received RST_STREAM with error code 3" in str(e) and "grpc_status:13" in str(e):
                    self._split_cache[key] = limit
                    result = self._query_batch(request, key=key, timeout=timeout, suggest_limit=math.ceil(limit / 2))
                else:
                    raise e
        res = []
        for d in result.documents:
            res.append(self._pb2doc(d))
        return res

    def _query_batch(self, req: olama_pb2.QueryRequest,
                     key: str,
                     timeout: Optional[float] = None,
                     suggest_limit: int = 512) -> olama_pb2.QueryResponse:
        result: Optional[olama_pb2.QueryResponse] = None
        ori_limit = req.query.limit
        ori_offset = req.query.offset
        for i in range(math.ceil(ori_limit / suggest_limit)):
            offset = ori_offset + i * suggest_limit
            limit = min(suggest_limit, ori_limit-i * suggest_limit)
            req.query.limit = limit
            req.query.offset = offset
            try:
                res: olama_pb2.QueryResponse = self.rpc_client.query(req, timeout=timeout)
            except GrpcException as e:
                if "Received RST_STREAM with error code 3" in str(e) and "grpc_status:13" in str(e):
                    self._split_cache[key] = limit
                    res: olama_pb2.QueryResponse = self._query_batch(req, key=key, timeout=timeout,
                                                                     suggest_limit=math.ceil(suggest_limit/2))
                else:
                    raise e
            if result is None:
                result = res
            else:
                result.documents.extend(res.documents)
        return result

    def count(self,
              database_name: str,
              collection_name: str,
              filter: Union[Filter, str] = None,
              timeout: float = None
              ) -> int:
        """Calculate the number of documents based on the query conditions."""
        request = olama_pb2.CountRequest(
            database=database_name,
            collection=collection_name,
        )
        if self.read_consistency is not None:
            request.readConsistency = self.read_consistency.value
        if filter is not None:
            request.query.filter = filter if isinstance(filter, str) else filter.cond
        result: olama_pb2.CountResponse = self.rpc_client.count(request, timeout=timeout)
        return result.count

    def search(self,
               database_name: str,
               collection_name: str,
               document_ids: Optional[List[str]] = None,
               vectors: Union[List[List[float]], ndarray] = None,
               embedding_items: List[str] = None,
               filter: Union[Filter, str] = None,
               params=None,
               retrieve_vector: bool = False,
               limit: int = 10,
               output_fields: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               return_pd_object=False,
               radius: Optional[float] = None,
               ) -> List[List[Union[Dict, olama_pb2.Document]]]:
        return self.search_with_warning(
            database_name=database_name,
            collection_name=collection_name,
            document_ids=document_ids,
            vectors=vectors,
            embedding_items=embedding_items,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
            return_pd_object=return_pd_object,
            radius=radius,
        ).get('documents')

    def search_with_warning(self,
                            database_name: str,
                            collection_name: str,
                            document_ids: Optional[List[str]] = None,
                            vectors: Union[List[List[float]], ndarray] = None,
                            embedding_items: List[str] = None,
                            filter: Union[Filter, str] = None,
                            params=None,
                            retrieve_vector: bool = False,
                            limit: int = 10,
                            output_fields: Optional[List[str]] = None,
                            timeout: Optional[float] = None,
                            return_pd_object=False,
                            radius: Optional[float] = None,
                            ) -> Dict[str, Any]:
        search = olama_pb2.SearchCond()
        batch = 0
        if vectors is not None:
            if isinstance(vectors, ndarray):
                vectors = vectors.tolist()
            for v in vectors:
                search.vectors.append(olama_pb2.VectorArray(vector=v))
            batch = len(search.vectors)
        if document_ids is not None:
            search.documentIds.extend(document_ids)
            batch = len(search.outputfields)
        if embedding_items is not None:
            search.embeddingItems.extend(embedding_items)
            batch = len(search.embeddingItems)
        if params is not None:
            if not isinstance(params, dict):
                params = vars(params)
            if params.get('ef') is not None:
                if params.get('ef') == 0:
                    raise ServerInternalError(code=15000,
                                              message=f'The value of ef cannot be 0.')
                search.params.ef = params.get('ef')
            if params.get('nprobe') is not None:
                search.params.nprobe = params.get('nprobe')
            if params.get('radius') is not None:
                search.params.radius = params.get('radius')
        if filter is not None:
            search.filter = filter if isinstance(filter, str) else filter.cond
        if output_fields is not None:
            search.outputfields.extend(output_fields)
        if retrieve_vector is not None:
            search.retrieveVector = retrieve_vector
        if limit is not None:
            search.limit = limit
        if radius is not None:
            search.range = True
            search.params.radius = radius
        request = olama_pb2.SearchRequest(
            database=database_name,
            collection=collection_name,
            readConsistency=self.read_consistency.value,
            search=search,
        )
        # res: olama_pb2.SearchResponse = self.rpc_client.search(request, timeout=timeout)
        key = f'search/{database_name}/{collection_name}/{batch}/{retrieve_vector}'
        split_size = self._split_cache.get(key, 163840)
        if limit >= split_size:
            res = self._search_by_split(self.rpc_client.search, request, timeout=timeout)
        else:
            try:
                res = self.rpc_client.search(request, timeout=timeout)
            except GrpcException as e:
                if "Received RST_STREAM with error code 3" in str(e) and "grpc_status:13" in str(e):
                    self._split_cache[key] = limit
                    res = self._search_by_split(self.rpc_client.search, request, timeout=timeout)
                else:
                    raise e
        rtl = []
        if return_pd_object:
            rtl = [r.documents for r in res.results]
        else:
            quick_trans = len(set(output_fields) - {'id', 'score'}) == 0 if output_fields else False
            for r in res.results:
                if quick_trans:
                    docs = [{"id": i.id, "score": i.score} for i in r.documents]
                else:
                    docs = []
                    for d in r.documents:
                        docs.append(self._pb2doc(d))
                rtl.append(docs)
        return {
            'warning': res.warning,
            'documents': rtl
        }

    def _search_cond(self,
                     ann: Optional[List[AnnSearch]] = None,
                     match: Optional[List[KeywordSearch]] = None,
                     filter: Union[Filter, str] = None,
                     rerank: Optional[Rerank] = None,
                     retrieve_vector: Optional[bool] = None,
                     output_fields: Optional[List[str]] = None,
                     limit: Optional[int] = None,
                     embedding_items: List[str] = None,
                     **kwargs
                     ):
        search = olama_pb2.SearchCond()
        ai = False
        if rerank is not None:
            search.rerank_params.method = rerank.method
            if isinstance(rerank, WeightedRerank):
                if rerank.field_list is not None and rerank.weight is not None:
                    for i in range(len(rerank.field_list)):
                        search.rerank_params.weights[rerank.field_list[i]] = rerank.weight[i]
            elif isinstance(rerank, RRFRerank):
                if rerank.k is not None:
                    if rerank.k == 0:
                        raise ServerInternalError(code=15000,
                                                  message=f'The value of rrf_k cannot be 0.')
                    search.rerank_params.rrf_k = rerank.k
        if match is not None:
            for m in match:
                md = olama_pb2.SparseData()
                if m.field_name is not None:
                    md.fieldName = m.field_name
                if m.limit is not None:
                    md.limit = m.limit
                data = m.data
                # hybrid_search sdk暂时不提供batch，但接口是batch
                if isinstance(data, list):
                    if len(data) == 0:
                        data = [data]
                    elif isinstance(data[0], list) \
                            and len(data[0]) > 0 and type(data[0][0]) == int:
                        data = [data]
                for item in data:
                    sva = olama_pb2.SparseVectorArray()
                    for pair in item:
                        svi = olama_pb2.SparseVecItem()
                        svi.term_id = pair[0]
                        svi.score = pair[1]
                        sva.sp_vector.append(svi)
                    md.data.append(sva)
                if m.terminate_after is not None:
                    md.params.terminateAfter = m.terminate_after
                if m.cutoff_frequency is not None:
                    md.params.cutoffFrequency = m.cutoff_frequency
                search.sparse.append(md)
        if filter is not None:
            search.filter = filter if isinstance(filter, str) else filter.cond
        if output_fields is not None:
            search.outputfields.extend(output_fields)
        if retrieve_vector is not None:
            search.retrieveVector = retrieve_vector
        if limit is not None:
            search.limit = limit
        if embedding_items is not None:
            search.embeddingItems.extend(embedding_items)
        if ann:
            d_type_str = False
            if len(ann) > 0:
                if isinstance(ann[0].data, str):
                    d_type_str = True
                    # ai = True
                elif isinstance(ann[0].data, list) and len(ann[0].data) > 0:
                    if isinstance(ann[0].data[0], str):
                        d_type_str = True
                        # ai = True
            for a in ann:
                ann_data = olama_pb2.AnnData()
                if a.field_name is not None:
                    ann_data.fieldName = a.field_name
                if a.document_ids is not None:
                    ann_data.documentIds.extend(a.document_ids)
                if a.data is not None:
                    data = a.data
                    if isinstance(data, str):
                        data = [data]
                    elif isinstance(data, list) and len(data) > 0 and type(data[0]) in (int, float, complex):
                        data = [data]
                    for v in data:
                        if isinstance(v, str):
                            if d_type_str:
                                ann_data.embeddingItems.append(v)
                            else:
                                raise ServerInternalError(
                                    code=14100,
                                    message="vector datatype must be same as the first vector's datatype vector")
                        else:
                            if d_type_str:
                                raise ServerInternalError(
                                    code=14100,
                                    message="vector datatype must be same as the first vector's datatype expression")
                            else:
                                ann_data.data.append(olama_pb2.VectorArray(vector=v))
                if a.params:
                    params = a.params
                    if not isinstance(params, dict):
                        params = vars(params)
                    if params.get('ef') is not None:
                        if params.get("ef") == 0:
                            raise ServerInternalError(code=15000,
                                                      message=f'The value of ef cannot be 0.')
                        ann_data.params.ef = params.get("ef")
                    if params.get('nprobe') is not None:
                        ann_data.params.nprobe = params.get("nprobe")
                    if params.get('radius') is not None:
                        ann_data.params.radius = params.get("radius")
                if a.limit is not None:
                    ann_data.limit = a.limit
                search.ann.append(ann_data)
        return search, ai

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
                      embedding_items: List[str] = None,
                      return_pd_object=False,
                      **kwargs) -> List[List[Union[Dict, olama_pb2.Document]]]:
        single = True
        batch = 0
        if ann:
            if isinstance(ann, List):
                single = False
            else:
                ann = [ann]
            batch = len(ann)
        if match:
            if isinstance(match, List):
                single = False
            else:
                match = [match]
            batch = len(match)
        search, ai = self._search_cond(
            ann=ann,
            match=match,
            filter=filter,
            rerank=rerank,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            embedding_items=embedding_items,
            **kwargs
        )
        request = olama_pb2.SearchRequest(
            database=database_name,
            collection=collection_name,
            readConsistency=self.read_consistency.value,
            search=search,
        )
        # res: olama_pb2.SearchResponse = self.rpc_client.hybrid_search(request, timeout=timeout, ai=ai)
        res: Optional[olama_pb2.SearchResponse] = None
        key = f'hybrid_search/{database_name}/{collection_name}/{batch}/{retrieve_vector}'
        split_size = self._split_cache.get(key, 163840)
        if limit >= split_size:
            res = self._search_by_split(self.rpc_client.hybrid_search, request, timeout=timeout, ai=ai)
        else:
            try:
                res = self.rpc_client.hybrid_search(request, timeout=timeout, ai=ai)
            except GrpcException as e:
                if "Received RST_STREAM with error code 3" in str(e) and "grpc_status:13" in str(e):
                    self._split_cache[key] = limit
                    res = self._search_by_split(self.rpc_client.hybrid_search, request, timeout=timeout, ai=ai)
                else:
                    raise e
        if 'warning' in res.warning:
            Warning(res.warning)
        rtl = []
        if return_pd_object:
            for r in res.results:
                rtl.append(r.documents)
        else:
            quick_trans = len(set(output_fields) - {'id', 'score'}) == 0 if output_fields else False
            for r in res.results:
                if quick_trans:
                    docs = [{"id": i.id, "score": i.score} for i in r.documents]
                else:
                    docs = []
                    for d in r.documents:
                        docs.append(self._pb2doc(d))
                rtl.append(docs)
        if single:
            rtl = rtl[0]
        return rtl

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
                        return_pd_object=False,
                        **kwargs) -> List[Union[Dict, olama_pb2.Document]]:
        match = KeywordSearch(
            field_name=field_name,
            data=data,
            terminate_after=terminate_after,
            cutoff_frequency=cutoff_frequency,
        )
        search, _ = self._search_cond(
            match=[match],
            filter=filter,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            **kwargs
        )
        request = olama_pb2.SearchRequest(
            database=database_name,
            collection=collection_name,
            readConsistency=self.read_consistency.value,
            search=search,
        )
        res: Optional[olama_pb2.SearchResponse] = None
        key = f'fulltext_search/{database_name}/{collection_name}/1/{retrieve_vector}'
        split_size = self._split_cache.get(key, 163840)
        if limit >= split_size:
            res = self._search_by_split(self.rpc_client.fulltext_search, request)
        else:
            try:
                res = self.rpc_client.fulltext_search(request)
            except GrpcException as e:
                if "Received RST_STREAM with error code 3" in str(e) and "grpc_status:13" in str(e):
                    self._split_cache[key] = limit
                    res = self._search_by_split(self.rpc_client.fulltext_search, request)
                else:
                    raise e
        if res.warning:
            Warning(res.warning)
        rtl = []
        if return_pd_object:
            for r in res.results:
                rtl.append(r.documents)
        else:
            quick_trans = len(set(output_fields) - {'id', 'score'}) == 0 if output_fields else False
            for r in res.results:
                if quick_trans:
                    docs = [{"id": i.id, "score": i.score} for i in r.documents]
                else:
                    docs = []
                    for d in r.documents:
                        docs.append(self._pb2doc(d))
                rtl.append(docs)
        return rtl[0]

    def _search_by_split(self,
                         function,
                         req: olama_pb2.SearchRequest,
                         timeout: Optional[float] = None,
                         ai: bool = False,
                         ) -> olama_pb2.SearchResponse:
        output_fields = list(req.search.outputfields)
        retrieve_vector = req.search.retrieveVector
        for i in range(len(req.search.outputfields)):
            req.search.outputfields.pop()
        req.search.outputfields.append('id')
        req.search.retrieveVector = False
        res: olama_pb2.SearchResponse = function(req, timeout=timeout, ai=ai)
        key = f'query/{req.database}/{req.collection}/{retrieve_vector}'
        for batch in res.results:
            query_req = olama_pb2.QueryRequest(
                database=req.database,
                collection=req.collection,
                query=olama_pb2.QueryCond(
                    retrieveVector=retrieve_vector,
                    offset=0,
                    outputFields=output_fields,
                )
            )
            doc_ids = [doc.id for doc in batch.documents]
            query_req.query.documentIds.extend(doc_ids)
            query_req.query.limit = len(doc_ids)
            query_limit = len(doc_ids)
            split_size = self._split_cache.get(key, 16385 * 2)
            while query_limit >= split_size:
                query_limit = math.ceil(query_limit/2)
            query_res = self._query_batch(query_req, key=key, suggest_limit=query_limit)
            for i, doc in enumerate(query_res.documents):
                doc.score = batch.documents[i].score
            for i in range(len(batch.documents)):
                batch.documents.pop()
            batch.documents.extend(query_res.documents)
        return res

    def _pb2doc(self, d: olama_pb2.Document) -> dict:
        doc = {
            'id': d.id,
        }
        if d.score is not None:
            doc['score'] = round(d.score, 5)
        if d.vector:
            doc['vector'] = list(d.vector)
        if d.sparse_vector:
            sp_vector = []
            for item in d.sparse_vector:
                sp_vector.append([item.term_id, item.score])
            doc['sparse_vector'] = sp_vector
        for k, v in d.fields.items():
            if v.HasField('val_str'):
                doc[k] = str(v.val_str, encoding='utf-8')
            elif v.HasField('val_u64'):
                doc[k] = v.val_u64
            elif v.HasField('val_double'):
                doc[k] = v.val_double
            elif v.HasField('val_str_arr'):
                arr = []
                for a in v.val_str_arr.str_arr:
                    arr.append(str(a, encoding='utf-8'))
                doc[k] = arr
            elif v.HasField('val_json'):
                doc[k] = ujson.loads(v.val_json)
            else:
                pass
        return doc

    def _doc2pb(self, doc: Union[Document, Dict]) -> olama_pb2.Document:
        doc_dict = doc if isinstance(doc, dict) else vars(doc)
        d = olama_pb2.Document()
        for k, v in doc_dict.items():
            if 'id' == k:
                d.id = v
            elif 'vector' == k:
                if isinstance(v, str):
                    d.data_expr = v
                else:
                    d.vector.extend(v)
            elif 'sparse_vector' == k:
                for sp in v:
                    d.sparse_vector.append(olama_pb2.SparseVecItem(
                        term_id=sp[0],
                        score=sp[1],
                    ))
            elif isinstance(v, int):
                if v < 0:
                    d.fields[k].val_double = v
                else:
                    d.fields[k].val_u64 = v
            elif isinstance(v, str):
                d.fields[k].val_str = bytes(v, encoding='utf-8')
            elif isinstance(v, list):
                al = []
                for arr in v:
                    al.append(bytes(arr, encoding='utf-8'))
                d.fields[k].val_str_arr.str_arr.extend(al)
            elif isinstance(v, dict):
                d.fields[k].val_json = bytes(ujson.dumps(v), encoding='utf-8')
            elif isinstance(v, float):
                d.fields[k].val_double = v
        return d

    def create_database(self, database_name: str, timeout: Optional[float] = None) -> RPCDatabase:
        req = olama_pb2.DatabaseRequest(database=database_name)
        rsp: olama_pb2.DatabaseResponse = self.rpc_client.create_database(req=req, timeout=timeout)
        return RPCDatabase(
            name=database_name,
            read_consistency=self.read_consistency,
            vdb_client=self,
        )

    def drop_database(self, database_name: str, timeout: Optional[float] = None) -> dict:
        req = olama_pb2.DatabaseRequest(database=database_name)
        rsp: olama_pb2.DatabaseResponse = self.rpc_client.drop_database(req=req, timeout=timeout)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
            "affectedCount": rsp.affectedCount,
        }

    def list_databases(self, timeout: Optional[float] = None) -> List[Union[RPCDatabase, AIDatabase]]:
        req = olama_pb2.DatabaseRequest()
        rsp: olama_pb2.DatabaseResponse = self.rpc_client.list_databases(req=req, timeout=timeout)
        dbs = []
        for db_name in rsp.databases:
            info_pb = rsp.info.get(db_name)
            info = {
                "count": info_pb.count,
                "createTime": info_pb.create_time,
            }
            if info_pb.db_type == olama_pb2.DataType.BASE:
                info["dbType"] = 'BASE_DB'
                dbs.append(RPCDatabase(name=db_name,
                                       vdb_client=self,
                                       read_consistency=self.read_consistency,
                                       info=info))
            else:
                info["dbType"] = 'AI_DB'
                dbs.append(AIDatabase(name=db_name,
                                      conn=None,
                                      read_consistency=self.read_consistency,
                                      info=info))
        return dbs

    def set_alias(self,
                  database_name: str,
                  collection_name: str,
                  collection_alias: str) -> Dict[str, Any]:
        req = olama_pb2.AddAliasRequest(database=database_name,
                                        collection=collection_name,
                                        alias=collection_alias)
        rsp: olama_pb2.UpdateAliasResponse = self.rpc_client.set_alias(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
            'affectedCount': rsp.affectedCount
        }

    def delete_alias(self, database_name: str, alias: str) -> Dict[str, Any]:
        req = olama_pb2.RemoveAliasRequest(database=database_name,
                                           alias=alias)
        rsp: olama_pb2.UpdateAliasResponse = self.rpc_client.delete_alias(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
            'affectedCount': rsp.affectedCount
        }

    def rebuild_index(self,
                      database_name: str,
                      collection_name: str,
                      drop_before_rebuild: bool = False,
                      throttle: Optional[int] = None,
                      timeout: Optional[float] = None,
                      field_name: Optional[str] = None):
        req = olama_pb2.RebuildIndexRequest(database=database_name,
                                            collection=collection_name,
                                            dropBeforeRebuild=drop_before_rebuild,
                                            )
        if throttle is None:
            req.throttle = 1
        if field_name:
            req.fieldName = field_name
        self.rpc_client.rebuild_index(req=req, timeout=timeout)

    def _field2pb(self,
                  index: Union[FilterIndex, VectorIndex, SparseIndex],
                  column: olama_pb2.IndexColumn):
        column.fieldName = index.name
        column.fieldType = index.field_type.value
        if index.indexType:
            column.indexType = index.indexType.value
        if hasattr(index, 'dimension') and index.dimension is not None:
            column.dimension = index.dimension
        if hasattr(index, 'param') and index.param is not None:
            param = index.param if index.param else {}
            param = vars(param) if hasattr(param, '__dict__') else param
            if param.get('M') is not None:
                if param.get('M') == 0:
                    raise ServerInternalError(code=15000,
                                              message=f'The value of M cannot be 0.')
                column.params.M = param.get('M')
            if param.get('efConstruction') is not None:
                if param.get('efConstruction') == 0:
                    raise ServerInternalError(code=15000,
                                              message=f'The value of efConstruction cannot be 0.')
                column.params.efConstruction = param.get('efConstruction')
            if param.get('nprobe') is not None:
                column.params.nprobe = param.get('nprobe')
            if param.get('nlist') is not None:
                if param.get('nlist') == 0:
                    raise ServerInternalError(code=15000,
                                              message=f'The value of nlist cannot be 0.')
                column.params.nlist = param.get('nlist', 0)
        if hasattr(index, 'metric_type') and index.metric_type is not None:
            column.metricType = index.metricType.value

    def add_index(self,
                  database_name: str,
                  collection_name: str,
                  indexes: List[FilterIndex],
                  build_existed_data: bool = True,
                  timeout: Optional[float] = None) -> dict:
        """Add scalar field index to existing collection."""
        req = olama_pb2.AddIndexRequest(database=database_name,
                                        collection=collection_name,
                                        buildExistedData=build_existed_data)
        for index in indexes:
            column: olama_pb2.IndexColumn = req.indexes[index.name]
            self._field2pb(index, column)
        rsp = self.rpc_client.add_index(req=req, timeout=timeout)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }

    def drop_index(self,
                   database_name: str,
                   collection_name: str,
                   field_names: List[str],
                   timeout: Optional[float] = None) -> dict:
        """Drop scalar field index from an existing collection."""
        req = olama_pb2.DropIndexRequest(database=database_name,
                                         collection=collection_name,
                                         )
        if not isinstance(field_names, list):
            raise ParamError(message='Invalid value for List[str] field: field_names')
        req.fieldNames.extend(field_names)
        rsp = self.rpc_client.drop_index(req=req, timeout=timeout)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }

    def modify_vector_index(self,
                            database_name: str,
                            collection_name: str,
                            vector_indexes: List[VectorIndex],
                            rebuild_rules: Optional[dict] = None,
                            timeout: Optional[float] = None) -> dict:
        """Adjust vector index parameters."""
        req = olama_pb2.ModifyVectorIndexRequest(database=database_name,
                                                 collection=collection_name,
                                                 rebuildRules=rebuild_rules)
        for index in vector_indexes:
            column: olama_pb2.IndexColumn = req.vectorIndexes[index.name]
            self._field2pb(index, column)
            if hasattr(index, 'field_type_none') and index.field_type_none:
                column.fieldType = ""
        if rebuild_rules is not None:
            if 'drop_before_rebuild' in rebuild_rules:
                rebuild_rules['dropBeforeRebuild'] = rebuild_rules.pop('drop_before_rebuild')
            if 'dropBeforeRebuild' in rebuild_rules:
                req.rebuildRules.dropBeforeRebuild = rebuild_rules.get('dropBeforeRebuild')
            if 'throttle' in rebuild_rules:
                req.rebuildRules.throttle = rebuild_rules.get('throttle')
        rsp = self.rpc_client.modify_vector_index(req=req, timeout=timeout)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }

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
                          ) -> RPCCollection:
        req = olama_pb2.CreateCollectionRequest(database=database_name,
                                                collection=collection_name,
                                                shardNum=shard,
                                                replicaNum=replicas)
        if description is not None:
            req.description = description
        if index is None and indexes:
            index = Index()
            for idx in indexes:
                index.add(idx)
        if index is not None:
            for f_name, f_item in index.indexes.items():
                column = req.indexes[f_name]
                column.fieldName = f_item.name
                if hasattr(f_item, 'field_type') and f_item.field_type is not None:
                    column.fieldType = f_item.field_type.value
                if hasattr(index, 'field_type_none') and index.field_type_none:
                    column.fieldType = FieldType.Vector.value
                if hasattr(f_item, 'indexType') and f_item.indexType is not None:
                    column.indexType = f_item.indexType.value
                if hasattr(f_item, 'dimension') and f_item.dimension is not None:
                    column.dimension = f_item.dimension
                if hasattr(f_item, 'param') and f_item.param is not None:
                    param = f_item.param if f_item.param else {}
                    param = vars(param) if hasattr(param, '__dict__') else param
                    column.params.M = param.get('M', 0)
                    column.params.efConstruction = param.get('efConstruction', 0)
                    column.params.nprobe = param.get('nprobe', 0)
                    column.params.nlist = param.get('nlist', 0)
                if hasattr(f_item, 'metric_type') and f_item.metric_type is not None:
                    column.metricType = f_item.metricType.value
                if f_item.field_type == FieldType.Array:
                    column.fieldElementType = 'string'
                if hasattr(f_item, 'auto_id') and f_item.auto_id is not None:
                    column.autoId = f_item.auto_id
        if embedding is not None:
            emb = vars(embedding)
            req.embeddingParams.field = emb.get('field')
            req.embeddingParams.vector_field = emb.get('vectorField')
            req.embeddingParams.model_name = emb.get('model')
        if ttl_config is not None:
            req.ttlConfig.enable = ttl_config.get('enable')
            req.ttlConfig.timeField = ttl_config.get('timeField')
        if filter_index_config is not None:
            if filter_index_config.filter_all is not None:
                req.filterIndexConfig.filterAll = filter_index_config.filter_all
            if filter_index_config.fields_without_index is not None:
                req.filterIndexConfig.fieldsWithoutIndex.extend(filter_index_config.fields_without_index)
            if filter_index_config.max_str_len is not None:
                if filter_index_config.max_str_len == 0:
                    raise ServerInternalError(code=15000,
                                              message=f'The value of maxStrLen cannot be 0.')
                req.filterIndexConfig.maxStrLen = filter_index_config.max_str_len
        rsp: olama_pb2.CreateCollectionResponse = self.rpc_client.create_collection(req=req, timeout=timeout)
        return RPCCollection(
            db=RPCDatabase(name=database_name,
                           read_consistency=self.read_consistency,
                           vdb_client=self),
            name=collection_name,
            shard=shard,
            replicas=replicas,
            description=description,
            index=index,
            embedding=embedding,
            read_consistency=self.read_consistency,
            ttl_config=ttl_config,
            vdb_client=self,
            filter_index_config=filter_index_config,
        )

    def drop_collection(self,
                        database_name: str,
                        collection_name: str,
                        timeout: Optional[float] = None) -> dict:
        req = olama_pb2.DropCollectionRequest(database=database_name,
                                              collection=collection_name)
        rsp: olama_pb2.DropCollectionResponse = self.rpc_client.drop_collection(req=req, timeout=timeout)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
            "affectedCount": rsp.affectedCount,
        }

    def list_collections(self,
                         database_name: str,
                         timeout: Optional[float] = None) -> List[RPCCollection]:
        req = olama_pb2.ListCollectionsRequest(database=database_name)
        rsp: olama_pb2.ListCollectionsResponse = self.rpc_client.list_collections(req=req, timeout=timeout)
        colls: List[RPCCollection] = []
        for coll in rsp.collections:
            colls.append(self._pb2coll(coll))
        return colls

    def _pb2coll(self, pb: olama_pb2.CreateCollectionRequest) -> RPCCollection:
        alias = pb.alias_list[0] if pb.alias_list else None
        ttl_config = None
        if pb.ttlConfig.enable:
            ttl_config = {}
            ttl_config['enable'] = pb.ttlConfig.enable
            ttl_config['timeField'] = pb.ttlConfig.timeField
        index = Index()
        for f_name, f_item in pb.indexes.items():
            field = {
                'fieldName': f_name,
                'fieldType': f_item.fieldType,
                'indexType': f_item.indexType,
            }
            if f_item.dimension:
                field['dimension'] = f_item.dimension
            if f_item.metricType:
                field['metricType'] = f_item.metricType
            if f_item.autoId:
                field['autoId'] = f_item.autoId
            if f_item.params:
                params = {}
                if f_item.params.nprobe:
                    params['nprobe'] = f_item.params.nprobe
                if f_item.params.M:
                    params['M'] = f_item.params.M
                if f_item.params.nlist:
                    params['nlist'] = f_item.params.nlist
                if f_item.params.efConstruction:
                    params['efConstruction'] = f_item.params.efConstruction
                if params:
                    field['params'] = params
            if f_item.fieldType == FieldType.Vector.value or f_item.fieldType == FieldType.BinaryVector.value:
                field['indexedCount'] = pb.size
            index.add(**field)
        embedding = None
        if pb.embeddingParams:
            if pb.embeddingParams.vector_field or pb.embeddingParams.field or pb.embeddingParams.model_name:
                embedding = Embedding(
                    vector_field=pb.embeddingParams.vector_field,
                    field=pb.embeddingParams.field,
                    model_name=pb.embeddingParams.model_name,
                    status="enabled",
                )
        filter_index_config = None
        if pb.filterIndexConfig:
            if not pb.filterIndexConfig.filterAll and \
                    len(pb.filterIndexConfig.fieldsWithoutIndex) == 0 and pb.filterIndexConfig.maxStrLen == 0:
                filter_index_config = None
            else:
                filter_index_config = FilterIndexConfig(
                    filter_all=pb.filterIndexConfig.filterAll,
                    fields_without_index=list(pb.filterIndexConfig.fieldsWithoutIndex),
                    max_str_len=pb.filterIndexConfig.maxStrLen,
                )
        return RPCCollection(
            db=RPCDatabase(name=pb.database,
                           read_consistency=self.read_consistency,
                           vdb_client=self),
            name=pb.collection,
            shard=pb.shardNum,
            replicas=pb.replicaNum,
            description=pb.description,
            index=index,
            embedding=embedding,
            read_consistency=self.read_consistency,
            ttl_config=ttl_config,
            vdb_client=self,
            createTime=pb.createTime,
            documentCount=pb.document_count,
            alias=alias,
            indexStatus={
                'status': pb.indexStatus.status,
                'startTime': pb.indexStatus.startTime,
            },
            filter_index_config=filter_index_config
        )

    def describe_collection(self,
                            database_name: str,
                            collection_name: str,
                            timeout: Optional[float] = None) -> RPCCollection:
        req = olama_pb2.DescribeCollectionRequest(database=database_name,
                                                  collection=collection_name)
        rsp: olama_pb2.DescribeCollectionResponse = self.rpc_client.describe_collection(req=req, timeout=timeout)
        col = self._pb2coll(rsp.collection)
        col.conn_name = collection_name
        return col

    def truncate_collection(self,
                            database_name: str,
                            collection_name: str) -> dict:
        req = olama_pb2.TruncateCollectionRequest(database=database_name,
                                                  collection=collection_name)
        rsp: olama_pb2.TruncateCollectionResponse = self.rpc_client.truncate_collection(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
            "affectedCount": rsp.affectedCount,
        }

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
        req = olama_pb2.UserAccountRequest(user=user,
                                           password=password)
        rsp: olama_pb2.UserAccountResponse = self.rpc_client.create_user(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }

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
        req = olama_pb2.UserAccountRequest(user=user)
        rsp: olama_pb2.UserAccountResponse = self.rpc_client.drop_user(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }

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
        req = olama_pb2.UserDescribeRequest(user=user)
        rsp: olama_pb2.UserDescribeResponse = self.rpc_client.describe_user(req=req)
        res = {
            'code': rsp.code,
            'msg': rsp.msg,
        }
        res.update(self._user_convert(rsp.user))
        return res

    def _user_convert(self, user: olama_pb2.User) -> dict:
        privileges = []
        for p in user.privileges:
            privileges.append({
                'resource': p.resource,
                'actions': list(p.actions),
            })
        res = {
            'user': user.name,
            'createTime': user.create_time,
            'privileges': privileges,
        }
        return res

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
        req = olama_pb2.UserListRequest()
        rsp: olama_pb2.UserListResponse = self.rpc_client.list_users(req=req)
        users = []
        for user in rsp.users:
            users.append(self._user_convert(user))
        return users

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
        req = olama_pb2.UserAccountRequest(user=user,
                                           password=password)
        rsp: olama_pb2.UserAccountResponse = self.rpc_client.change_password(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }

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
        req = olama_pb2.UserPrivilegesRequest(user=user)
        privileges = privileges if isinstance(privileges, list) else [privileges]
        for pri in privileges:
            actions = pri.get('actions')
            if actions is not None and not isinstance(actions, list):
                raise ServerInternalError(code=15000, message='actions must be an ARRAY')
            req.privileges.append(olama_pb2.Privilege(
                resource=pri.get('resource'),
                actions=actions,
            ))
        rsp: olama_pb2.UserPrivilegesResponse = self.rpc_client.grant_permission(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }

    def revoke_from_user(self,
                         user: str,
                         privileges: Union[dict, List[dict]]) -> dict:
        """Revoke permission for user.

        Args:
            user (str): The user to grant permission.
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
        req = olama_pb2.UserPrivilegesRequest(user=user)
        privileges = privileges if isinstance(privileges, list) else [privileges]
        for pri in privileges:
            actions = pri.get('actions')
            if actions is not None and not isinstance(actions, list):
                raise ServerInternalError(code=15000, message='actions must be an ARRAY')
            req.privileges.append(olama_pb2.Privilege(
                resource=pri.get('resource'),
                actions=actions,
            ))
        rsp: olama_pb2.UserPrivilegesResponse = self.rpc_client.revoke_permission(req=req)
        return {
            "code": rsp.code,
            "msg": rsp.msg,
        }
