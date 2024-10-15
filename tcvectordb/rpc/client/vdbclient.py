from typing import List, Union, Dict, Optional, Any

from numpy import ndarray

from tcvectordb.exceptions import ServerInternalError
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.collection import Embedding
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank, WeightedRerank, RRFRerank
from tcvectordb.model.enum import ReadConsistency, FieldType, IndexType, MetricType
from tcvectordb.model.index import Index
from tcvectordb.rpc.client.rpcclient import RPCClient
from tcvectordb.rpc.model.collection import RPCCollection
from tcvectordb.rpc.model.database import RPCDatabase
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
               filter: Union[Filter, str] = None,
               timeout: float = None):
        query = olama_pb2.QueryCond()
        if document_ids is not None:
            query.documentIds.extend(document_ids)
        if filter is not None:
            query.filter = filter if isinstance(filter, str) else filter.cond
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
              timeout: Optional[float] = None) -> List[Dict]:
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
               vectors: Union[List[List[float]], ndarray] = None,
               embedding_items: List[str] = None,
               filter: Union[Filter, str] = None,
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
                            vectors: Union[List[List[float]], ndarray] = None,
                            embedding_items: List[str] = None,
                            filter: Union[Filter, str] = None,
                            params=None,
                            retrieve_vector: bool = False,
                            limit: int = 10,
                            output_fields: Optional[List[str]] = None,
                            timeout: Optional[float] = None,
                            ) -> Dict[str, Any]:
        search = olama_pb2.SearchCond()
        if vectors is not None:
            if isinstance(vectors, ndarray):
                vectors = vectors.tolist()
            for v in vectors:
                search.vectors.append(olama_pb2.VectorArray(vector=v))
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
            search.filter = filter if isinstance(filter, str) else filter.cond
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
                    elif isinstance(data, list) and len(data) > 0 and type(data[0]) in (int, float, complex):
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
                      ann: Optional[Union[List[AnnSearch], AnnSearch]] = None,
                      match: Optional[Union[List[KeywordSearch], KeywordSearch]] = None,
                      filter: Union[Filter, str] = None,
                      rerank: Optional[Rerank] = None,
                      retrieve_vector: Optional[bool] = None,
                      output_fields: Optional[List[str]] = None,
                      limit: Optional[int] = None,
                      timeout: Optional[float] = None,
                      embedding_items: List[str] = None,
                      **kwargs) -> List[List[Dict]]:
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
            rtl.append(docs)
        if single:
            rtl = rtl[0]
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

    def create_database(self, database_name: str, timeout: Optional[float] = None) -> RPCDatabase:
        req = olama_pb2.DatabaseRequest(database=database_name)
        rsp: olama_pb2.DatabaseResponse = self.rpc_client.create_database(req=req, timeout=timeout)
        return RPCDatabase(
            name=database_name,
            read_consistency=self.read_consistency,
            vdb_client=self,
            db_type='BASE',
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
            info = rsp.info.get(db_name)
            if info.db_type == olama_pb2.DataType.BASE:
                dbs.append(RPCDatabase(name=db_name,
                                       vdb_client=self,
                                       read_consistency=self.read_consistency,
                                       db_type='BASE'))
            else:
                dbs.append(AIDatabase(name=db_name,
                                      conn=None,
                                      read_consistency=self.read_consistency,
                                      db_type='AI_DOC'))
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
                      throttle: int = 0,
                      timeout: Optional[float] = None):
        req = olama_pb2.RebuildIndexRequest(database=database_name,
                                            collection=collection_name,
                                            dropBeforeRebuild=drop_before_rebuild,
                                            throttle=throttle)
        self.rpc_client.rebuild_index(req=req, timeout=timeout)

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
                          ) -> RPCCollection:
        req = olama_pb2.CreateCollectionRequest(database=database_name,
                                                collection=collection_name,
                                                shardNum=shard,
                                                replicaNum=replicas)
        if description is not None:
            req.description = description
        if index is not None:
            for f_name, f_item in index.indexes.items():
                column = req.indexes[f_name]
                column.fieldName = f_item.name
                column.fieldType = f_item.field_type.value
                column.indexType = f_item.indexType.value
                if f_item.field_type == FieldType.Vector:
                    column.dimension = f_item.dimension
                    param = f_item.param if f_item.param else {}
                    param = vars(param) if hasattr(param, '__dict__') else param
                    column.params.M = param.get('M', 0)
                    column.params.efConstruction = param.get('efConstruction', 0)
                    column.params.nprobe = param.get('nprobe', 0)
                    column.params.nlist = param.get('nlist', 0)
                if f_item.field_type in (FieldType.Vector, FieldType.SparseVector):
                    column.metricType = f_item.metricType.value
        if embedding is not None:
            emb = vars(embedding)
            req.embeddingParams.field = emb.get('field')
            req.embeddingParams.vector_field = emb.get('vectorField')
            req.embeddingParams.model_name = emb.get('model')
        if ttl_config is not None:
            req.ttlConfig.enable = ttl_config.get('enable')
            req.ttlConfig.timeField = ttl_config.get('timeField')
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
            # rpc 没有返回indexedCount
            # if f_item.fieldType == FieldType.Vector.value:
            #     field['indexedCount'] = f_item
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
            documentCount=pb.size,
            alias=alias,
            indexStatus={
                'indexStatus': pb.indexStatus.status,
                'startTime': pb.indexStatus.startTime,
            }
        )

    def describe_collection(self,
                            database_name: str,
                            collection_name: str,
                            timeout: Optional[float] = None) -> RPCCollection:
        req = olama_pb2.DescribeCollectionRequest(database=database_name,
                                                  collection=collection_name)
        rsp: olama_pb2.DescribeCollectionResponse = self.rpc_client.describe_collection(req=req, timeout=timeout)
        return self._pb2coll(rsp.collection)

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
