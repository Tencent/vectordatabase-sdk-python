from typing import List, Union, Dict, Optional, Any

from tcvectordb.exceptions import ServerInternalError
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank, WeightedRerank, RRFRerank
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.rpc.client.rpcclient import RPCClient
from tcvectordb.rpc.proto import olama_pb2


class VdbClient:
    def __init__(self,
                 client: RPCClient,
                 read_consistency: ReadConsistency,
                 ):
        self.rpc_client = client
        self.read_consistency = read_consistency

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
               filter: Filter = None,
               timeout: float = None):
        query = olama_pb2.QueryCond()
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter.cond
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
               filter: Optional[Filter] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None):
        query = olama_pb2.QueryCond()
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter.cond
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
              filter: Optional[Filter] = None,
              output_fields: Optional[List[str]] = None,
              timeout: Optional[float] = None) -> List[Dict]:
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
            database=database_name,
            collection=collection_name,
            query=query,
            readConsistency=self.read_consistency.value,
        )
        result: olama_pb2.QueryResponse = self.rpc_client.query(request, timeout=timeout)
        res = []
        for d in result.documents:
            res.append(self._pb2doc(d))
        return res

    def search(self,
               database_name: str,
               collection_name: str,
               document_ids: Optional[List[str]] = None,
               vectors: Optional[List[List[float]]] = None,
               embedding_items: List[str] = None,
               filter: Filter = None,
               params=None,
               retrieve_vector: bool = False,
               limit: int = 10,
               output_fields: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ) -> List[List[Dict]]:
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
        ).get('documents')

    def search_with_warning(self,
                            database_name: str,
                            collection_name: str,
                            document_ids: Optional[List[str]] = None,
                            vectors: Optional[List[List[float]]] = None,
                            embedding_items: List[str] = None,
                            filter: Filter = None,
                            params=None,
                            retrieve_vector: bool = False,
                            limit: int = 10,
                            output_fields: Optional[List[str]] = None,
                            timeout: Optional[float] = None,
                            ) -> Dict[str, Any]:
        search = olama_pb2.SearchCond()
        ai = False
        if vectors is not None:
            search, ai = self._search_cond(
                ann=[AnnSearch(
                    field_name="vector",
                    # ann暂时不对外暴露batch
                    data=vectors,
                    params=params,
                )],
                filter=filter,
                retrieve_vector=retrieve_vector,
                limit=limit,
                output_fields=output_fields,
            )
        else:
            if document_ids is not None:
                search.documentIds.extend(document_ids)
            if embedding_items is not None:
                search.embeddingItems.extend(embedding_items)
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
            database=database_name,
            collection=collection_name,
            readConsistency=self.read_consistency.value,
            search=search,
        )
        res: olama_pb2.SearchResponse = self.rpc_client.search(request, timeout=timeout, ai=ai)
        rtl = []
        for r in res.results:
            docs = []
            for d in r.documents:
                docs.append(self._pb2doc(d))
            if docs:
                rtl.append(docs)
        return {
            'warning': res.warning,
            'documents': rtl
        }

    def _search_cond(self,
                     ann: Optional[List[AnnSearch]] = None,
                     match: Optional[List[KeywordSearch]] = None,
                     filter: Optional[Filter] = None,
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
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list) \
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
                search.sparse.append(md)
        if filter is not None:
            search.filter = filter.cond
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
                    ai = True
                elif isinstance(ann[0].data, list) and len(ann[0].data) > 0:
                    if isinstance(ann[0].data[0], str):
                        d_type_str = True
                        ai = True
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
                    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], float):
                        data = [data]
                    for v in data:
                        if isinstance(v, str):
                            if d_type_str:
                                ann_data.data_expr.append(v)
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
                      ann: Optional[List[AnnSearch]] = None,
                      match: Optional[List[KeywordSearch]] = None,
                      filter: Optional[Filter] = None,
                      rerank: Optional[Rerank] = None,
                      retrieve_vector: Optional[bool] = None,
                      output_fields: Optional[List[str]] = None,
                      limit: Optional[int] = None,
                      timeout: Optional[float] = None,
                      embedding_items: List[str] = None,
                      **kwargs) -> List[List[Dict]]:
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
        res: olama_pb2.SearchResponse = self.rpc_client.hybrid_search(request, timeout=timeout, ai=ai)
        if 'warning' in res.warning:
            Warning(res.warning)
        rtl = []
        for r in res.results:
            docs = []
            for d in r.documents:
                docs.append(self._pb2doc(d))
            if docs:
                rtl.append(docs)
        return rtl

    def _pb2doc(self, d: olama_pb2.Document) -> dict:
        doc = {
            'id': d.id,
        }
        if d.score is not None:
            doc['score'] = d.score
        if d.vector:
            vecs = []
            for v in d.vector:
                vecs.append(v.real)
            doc['vector'] = vecs
        if d.sparse_vector:
            sp_vector = []
            for item in d.sparse_vector:
                sp_vector.append([item.term_id, item.score])
            doc['sparse_vector'] = sp_vector
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
                d.fields[k].val_u64 = v
            elif isinstance(v, str):
                d.fields[k].val_str = bytes(v, encoding='utf-8')
            elif isinstance(v, list):
                al = []
                for arr in v:
                    al.append(bytes(arr, encoding='utf-8'))
                d.fields[k].val_str_arr.str_arr.extend(al)
        return d
