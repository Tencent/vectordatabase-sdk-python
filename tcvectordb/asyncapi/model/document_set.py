from typing import Dict, Any, Optional, List

from tcvectordb.model.document_set import Chunk, DocumentSet


class AsyncDocumentSet(DocumentSet):
    """Async wrap of DocumentSet"""

    def __init__(self,
                 collection_view,
                 id: str,
                 name: str,
                 text_prefix: str = None,
                 text: str = None,
                 text_length: Optional[int] = None,
                 byte_length: Optional[int] = None,
                 indexed_progress: Optional[int] = None,
                 indexed_status: Optional[str] = None,
                 create_time: Optional[str] = None,
                 last_update_time: Optional[str] = None,
                 keywords: Optional[str] = None,
                 indexed_error_msg: Optional[str] = None,
                 splitter_process=None,
                 parsing_process=None,
                 **kwargs) -> None:
        super().__init__(collection_view=collection_view,
                         id=id,
                         name=name,
                         text_prefix=text_prefix,
                         text=text,
                         text_length=text_length,
                         byte_length=byte_length,
                         indexed_progress=indexed_progress,
                         indexed_status=indexed_status,
                         create_time=create_time,
                         last_update_time=last_update_time,
                         keywords=keywords,
                         indexed_error_msg=indexed_error_msg,
                         splitter_process=splitter_process,
                         parsing_process=parsing_process,
                         **kwargs,)

    async def get_text(self) -> str:
        ds = await self.collection_view.get_document_set(document_set_id=self.id)
        self.load_fields(vars(ds))
        return self.text

    async def delete(self) -> Dict[str, Any]:
        return await self.collection_view.delete(document_set_id=self.id)

    async def get_chunks(self,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None,
                         timeout: Optional[float] = None,
                         ) -> List[Chunk]:
        return await self.collection_view.get_chunks(document_set_id=self.id,
                                                     document_set_name=self.name,
                                                     limit=limit,
                                                     offset=offset,
                                                     timeout=timeout)
