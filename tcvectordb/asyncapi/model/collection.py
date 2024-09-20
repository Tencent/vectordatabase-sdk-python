from typing import Dict, List, Optional, Any, Union

from tcvectordb.model.collection import Collection
from tcvectordb.model.collection_view import Embedding
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index


class AsyncCollection(Collection):

    def __init__(self,
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
        super().__init__(db,
                         name,
                         shard,
                         replicas,
                         description,
                         index,
                         embedding,
                         read_consistency,
                         **kwargs)

    async def upsert(self,
                     documents: List[Union[Document, Dict]],
                     timeout: Optional[float] = None,
                     build_index: bool = True,
                     **kwargs
                     ):
        return super().upsert(documents,
                              timeout,
                              build_index,
                              **kwargs)

    async def query(self,
                    document_ids: Optional[List] = None,
                    retrieve_vector: bool = False,
                    limit: Optional[int] = None,
                    offset: Optional[int] = None,
                    filter: Optional[Filter] = None,
                    output_fields: Optional[List[str]] = None,
                    timeout: Optional[float] = None,
                    ) -> List[Dict]:
        return super().query(document_ids,
                             retrieve_vector,
                             limit,
                             offset,
                             filter,
                             output_fields,
                             timeout)

    async def search(self,
                     vectors: List[List[float]],
                     filter: Filter = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     ) -> List[List[Dict]]:
        return super().search(vectors,
                              filter,
                              params,
                              retrieve_vector,
                              limit,
                              output_fields,
                              timeout)

    async def searchById(self,
                         document_ids: List,
                         filter: Filter = None,
                         params=None,
                         retrieve_vector: bool = False,
                         limit: int = 10,
                         timeout: Optional[float] = None,
                         output_fields: Optional[List[str]] = None
                         ) -> List[List[Dict]]:
        return super().searchById(document_ids,
                                  filter,
                                  params,
                                  retrieve_vector,
                                  limit,
                                  timeout,
                                  output_fields)

    async def searchByText(self,
                           embeddingItems: List[str],
                           filter: Filter = None,
                           params=None,
                           retrieve_vector: bool = False,
                           limit: int = 10,
                           output_fields: Optional[List[str]] = None,
                           timeout: Optional[float] = None,
                           ) -> Dict[str, Any]:
        return super().searchByText(embeddingItems,
                                    filter,
                                    params,
                                    retrieve_vector,
                                    limit,
                                    output_fields,
                                    timeout)

    async def hybrid_search(self,
                            ann: Optional[List[AnnSearch]] = None,
                            match: Optional[List[KeywordSearch]] = None,
                            filter: Optional[Filter] = None,
                            rerank: Optional[Rerank] = None,
                            retrieve_vector: Optional[bool] = None,
                            output_fields: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            timeout: Optional[float] = None,
                            **kwargs) -> List[List[Dict]]:
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

    async def delete(self,
                     document_ids: List[str] = None,
                     filter: Filter = None,
                     timeout: float = None,
    ):
        return super().delete(document_ids, filter, timeout)

    async def update(self,
                     data: Union[Document, Dict],
                     filter: Optional[Filter] = None,
                     document_ids: Optional[List[str]] = None,
                     timeout: Optional[float] = None):
        return super().update(data, filter, document_ids, timeout)

    async def rebuild_index(self,
                            drop_before_rebuild: bool = False,
                            throttle: int = 0,
                            timeout: Optional[float] = None):
        super().rebuild_index(drop_before_rebuild, throttle, timeout)
