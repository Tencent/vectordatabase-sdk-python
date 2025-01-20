from typing import Optional, List, Union

from tcvectordb.asyncapi.model.document_set import AsyncDocumentSet
from tcvectordb.model.collection_view import SplitterProcess, CollectionView, Embedding, ParsingProcess
from tcvectordb.model.document import Filter, Document
from tcvectordb.model.document_set import Rerank, SearchResult, Chunk, DocumentSet
from tcvectordb.model.index import Index


class AsyncCollectionView(CollectionView):
    """Async wrap of CollectionView"""

    def __init__(self,
                 db,
                 name: str,
                 description: str = '',
                 embedding: Optional[Embedding] = None,
                 splitter_process: Optional[SplitterProcess] = None,
                 index: Optional[Index] = None,
                 expected_file_num: Optional[int] = None,
                 average_file_size: Optional[int] = None,
                 shard: Optional[int] = None,
                 replicas: Optional[int] = None,
                 parsing_process: Optional[ParsingProcess] = None,
                 ):
        super().__init__(db,
                         name,
                         description,
                         embedding,
                         splitter_process,
                         index,
                         expected_file_num=expected_file_num,
                         average_file_size=average_file_size,
                         shard=shard,
                         replicas=replicas,
                         parsing_process=parsing_process)

    async def load_and_split_text(self,
                                  local_file_path: str,
                                  document_set_name: Optional[str] = None,
                                  metadata: Optional[dict] = None,
                                  splitter_process: Optional[SplitterProcess] = None,
                                  timeout: Optional[float] = None,
                                  parsing_process: Optional[ParsingProcess] = None) -> AsyncDocumentSet:
        ds = super().load_and_split_text(local_file_path,
                                         document_set_name,
                                         metadata,
                                         splitter_process,
                                         timeout,
                                         parsing_process=parsing_process)
        return ds_convert(ds)

    async def search(self,
                     content: str,
                     document_set_name: Optional[List[str]] = None,
                     expand_chunk: Optional[list] = None,
                     rerank: Optional[Rerank] = None,
                     filter: Union[Filter, str] = None,
                     limit: Optional[int] = None,
                     timeout: Optional[float] = None,
                     ) -> List[SearchResult]:
        return super().search(content,
                              document_set_name,
                              expand_chunk,
                              rerank,
                              filter,
                              limit,
                              timeout)

    async def query(self,
                    document_set_id: Optional[List] = None,
                    document_set_name: Optional[List[str]] = None,
                    filter: Union[Filter, str] = None,
                    limit: Optional[int] = None,
                    offset: Optional[int] = None,
                    output_fields: Optional[List[str]] = None,
                    timeout: Optional[float] = None,
                    ) -> List[AsyncDocumentSet]:
        dss = super().query(document_set_id,
                            document_set_name,
                            filter,
                            limit,
                            offset,
                            output_fields,
                            timeout)
        return [ds_convert(ds) for ds in dss]

    async def get_document_set(self,
                               document_set_id: Optional[str] = None,
                               document_set_name: Optional[str] = None,
                               timeout: Optional[float] = None,) -> Union[AsyncDocumentSet, None]:
        ds = super().get_document_set(document_set_id,
                                      document_set_name,
                                      timeout)
        if ds:
            ds = ds_convert(ds)
        return ds

    async def delete(self,
                     document_set_id: Union[str, List[str]] = None,
                     document_set_name: Union[str, List[str]] = None,
                     filter: Union[Filter, str] = None,
                     timeout: float = None,
                     ):
        return super().delete(document_set_id,
                              document_set_name,
                              filter,
                              timeout)

    async def update(self,
                     data: Document,
                     document_set_id: Union[str, List[str]] = None,
                     document_set_name: Union[str, List[str]] = None,
                     filter: Union[Filter, str] = None,
                     timeout: float = None,
                     ):
        return super().update(data,
                              document_set_id,
                              document_set_name,
                              filter,
                              timeout)

    async def get_chunks(self,
                         document_set_id: Optional[str] = None,
                         document_set_name: Optional[str] = None,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None,
                         timeout: Optional[float] = None,
                         ) -> List[Chunk]:
        return super().get_chunks(document_set_id,
                                  document_set_name,
                                  limit,
                                  offset,
                                  timeout)


def ds_convert(ds: DocumentSet) -> AsyncDocumentSet:
    return AsyncDocumentSet(
        collection_view=ds.collection_view,
        id=ds.id,
        name=ds.name,
        text_prefix=ds.text_prefix,
        text=ds.text,
        text_length=ds.document_set_info.text_length,
        byte_length=ds.document_set_info.byte_length,
        indexed_progress=ds.document_set_info.indexed_progress,
        indexed_status=ds.document_set_info.indexed_status,
        create_time=ds.document_set_info.create_time,
        last_update_time=ds.document_set_info.last_update_time,
        keywords=ds.document_set_info.keywords,
        indexed_error_msg=ds.document_set_info.indexed_error_msg,
        splitter_process=ds.splitter_process,
        parsing_process=ds.parsing_process,
        **ds.__getattribute__('_scalar_fields'),
    )
