from typing import Dict, List, Optional, Any, Union

from numpy import ndarray

from tcvectordb.model.collection import Collection
from tcvectordb.model.collection_view import Embedding
from tcvectordb.model.document import Document, Filter, AnnSearch, KeywordSearch, Rerank
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index
# from tcvectordb.rpc.client.vdbclient import VdbClient


class RPCCollection(Collection):
# class RPCCollection:

    def __init__(self,
                 db,
                 name: str = '',
                 shard=0,
                 replicas=0,
                 description='',
                 index: Index = None,
                 embedding: Embedding = None,
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 vdb_client=None,
                 ttl_config: dict = None,
                 **kwargs):
        super().__init__(db,
                         name,
                         shard,
                         replicas,
                         description,
                         index,
                         embedding,
                         read_consistency,
                         ttl_config=ttl_config,
                         **kwargs)
        self.vdb_client = vdb_client

    def upsert(self,
               documents: List[Union[Document, Dict]],
               timeout: Optional[float] = None,
               build_index: bool = True,
               **kwargs):
        return self.vdb_client.upsert(
            database_name=self.database_name,
            collection_name=self.collection_name,
            documents=documents,
            timeout=timeout,
            build_index=build_index,
            **kwargs
        )

    def query(self,
              document_ids: Optional[List] = None,
              retrieve_vector: bool = False,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              filter: Union[Filter, str] = None,
              output_fields: Optional[List[str]] = None,
              timeout: Optional[float] = None,
              ) -> List[Dict]:
        return self.vdb_client.query(
            database_name=self.database_name,
            collection_name=self.collection_name,
            document_ids=document_ids,
            retrieve_vector=retrieve_vector,
            limit=limit,
            offset=offset,
            filter=filter,
            output_fields=output_fields,
            timeout=timeout,
        )

    def delete(self,
               document_ids: List[str] = None,
               filter: Union[Filter, str] = None,
               timeout: float = None,
               ):
        return self.vdb_client.delete(
            database_name=self.database_name,
            collection_name=self.collection_name,
            document_ids=document_ids,
            filter=filter,
            timeout=timeout,
        )

    def update(self,
               data: Union[Document, Dict],
               filter: Union[Filter, str] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ):
        return self.vdb_client.update(
            database_name=self.database_name,
            collection_name=self.collection_name,
            data=data,
            filter=filter,
            document_ids=document_ids,
            timeout=timeout,
        )

    def search(self,
               vectors: Union[List[List[float]], ndarray],
               filter: Union[Filter, str] = None,
               params=None,
               retrieve_vector: bool = False,
               limit: int = 10,
               output_fields: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ) -> List[List[Dict]]:
        return self.vdb_client.search(
            database_name=self.database_name,
            collection_name=self.collection_name,
            vectors=vectors,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def searchById(self,
                   document_ids: List,
                   filter: Union[Filter, str] = None,
                   params=None,
                   retrieve_vector: bool = False,
                   limit: int = 10,
                   timeout: Optional[float] = None,
                   output_fields: Optional[List[str]] = None
    ) -> List[List[Dict]]:
        return self.vdb_client.search(
            database_name=self.database_name,
            collection_name=self.collection_name,
            document_ids=document_ids,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            timeout=timeout,
            output_fields=output_fields,
        )

    def searchByText(self,
                     embeddingItems: List[str],
                     filter: Union[Filter, str] = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     ) -> Dict[str, Any]:
        return self.vdb_client.search_with_warning(
            database_name=self.database_name,
            collection_name=self.collection_name,
            embedding_items=embeddingItems,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def hybrid_search(self,
                      ann: Optional[Union[List[AnnSearch], AnnSearch]] = None,
                      match: Optional[Union[List[KeywordSearch], KeywordSearch]] = None,
                      filter: Union[Filter, str] = None,
                      rerank: Optional[Rerank] = None,
                      retrieve_vector: Optional[bool] = None,
                      output_fields: Optional[List[str]] = None,
                      limit: Optional[int] = None,
                      timeout: Optional[float] = None,
                      **kwargs) -> List[List[Dict]]:
        return self.vdb_client.hybrid_search(
            database_name=self.database_name,
            collection_name=self.collection_name,
            ann=ann,
            match=match,
            filter=filter,
            rerank=rerank,
            retrieve_vector=retrieve_vector,
            output_fields=output_fields,
            limit=limit,
            timeout=timeout,
            **kwargs)

    def rebuild_index(self,
                      drop_before_rebuild: bool = False,
                      throttle: int = 0,
                      timeout: Optional[float] = None):
        self.vdb_client.rebuild_index(database_name=self.database_name,
                                      collection_name=self.collection_name,
                                      drop_before_rebuild=drop_before_rebuild,
                                      throttle=throttle,
                                      timeout=timeout)
