from enum import Enum, unique
from typing import Dict, Any, Optional, List, Union

from tcvectordb.model.document import Filter


class Chunk:
    """Chunk"""

    def __init__(self, start_pos: int, end_pos: int, text: str):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.text = text

    @property
    def __dict__(self):
        res = {
            "startPos": self.start_pos,
            "endPos": self.end_pos,
        }
        if self.text:
            res['text'] = self.text
        return res


class DocumentSet:
    """DocumentSet is a collection of multiple documents that have been split from a single file."""

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
        self.collection_view = collection_view
        self.id = id
        self.name = name
        self.text = text
        self.text_prefix = text_prefix
        self.document_set_info = DocumentSetInfo(
            text_length=text_length,
            byte_length=byte_length,
            indexed_status=indexed_status,
            indexed_progress=indexed_progress,
            create_time=create_time,
            last_update_time=last_update_time,
            keywords=keywords,
            indexed_error_msg=indexed_error_msg,
        )
        self.splitter_process = splitter_process
        self.parsing_process = parsing_process
        self._scalar_fields = None
        self._set_scalar_fields(kwargs)

    @property
    def __dict__(self):
        res = {
            "documentSetId": self.id,
            "documentSetName": self.name,
        }
        if self.text_prefix:
            res['textPrefix'] = self.text_prefix
        if self.text:
            res['text'] = self.text
        if self.document_set_info and vars(self.document_set_info):
            res['documentSetInfo'] = vars(self.document_set_info)
        if self.splitter_process:
            res['splitterPreprocess'] = vars(self.splitter_process)
        if self.parsing_process:
            res['parsingProcess'] = vars(self.parsing_process)
        if self._scalar_fields:
            res.update(self._scalar_fields)
        return res

    def _set_scalar_fields(self, data: dict):
        if 'documentSetId' in data:
            data.pop('documentSetId')
        if 'documentSetName' in data:
            data.pop('documentSetName')
        if 'documentSetInfo' in data:
            data.pop('documentSetInfo')
        if 'textPrefix' in data:
            data.pop('textPrefix')
        if 'text' in data:
            data.pop('text')
        if 'splitterPreprocess' in data:
            data.pop('splitterPreprocess')
        if 'parsingProcess' in data:
            data.pop('parsingProcess')
        self._scalar_fields = data

    def load_fields(self, data: dict, splitter_process=None, parsing_process=None):
        self.text_prefix = data.get('textPrefix')
        self.text = data.get('text')
        if 'documentSetInfo' in data:
            info = data['documentSetInfo']
            dsi = DocumentSetInfo(
                text_length=info.get('textLength'),
                byte_length=info.get('byteLength'),
                indexed_status=info.get('indexedStatus'),
                indexed_progress=info.get('indexedProgress'),
                create_time=info.get('createTime'),
                last_update_time=info.get('lastUpdateTime'),
                keywords=info.get('keywords'),
                indexed_error_msg=info.get('indexedErrorMsg')
            )
            self.document_set_info = dsi
        if splitter_process is not None:
            self.splitter_process = splitter_process
        if parsing_process is not None:
            self.parsing_process = parsing_process
        self._set_scalar_fields(data)

    def get_text(self) -> str:
        ds = self.collection_view.get_document_set(document_set_id=self.id)
        self.load_fields(vars(ds))
        return self.text

    def delete(self) -> Dict[str, Any]:
        return self.collection_view.delete(document_set_id=self.id)

    def get_chunks(self,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None,
                   timeout: Optional[float] = None,
                   ) -> List[Chunk]:
        return self.collection_view.get_chunks(document_set_id=self.id,
                                               document_set_name=self.name,
                                               limit=limit,
                                               offset=offset,
                                               timeout=timeout)


class DocumentSetInfo:
    def __init__(self,
                 text_length: Optional[int] = None,
                 byte_length: Optional[int] = None,
                 indexed_progress: Optional[int] = None,
                 indexed_status: Optional[str] = None,
                 create_time: Optional[str] = None,
                 last_update_time: Optional[str] = None,
                 keywords: Optional[str] = None,
                 indexed_error_msg: Optional[str] = None):
        self.text_length: Optional[int] = text_length
        self.byte_length: Optional[int] = byte_length
        self.indexed_progress: Optional[int] = indexed_progress
        # Ready | New | Loading | Failure
        self.indexed_status: Optional[str] = indexed_status
        self.create_time: Optional[str] = create_time
        self.last_update_time: Optional[str] = last_update_time
        self.keywords = keywords
        self.indexed_error_msg = indexed_error_msg

    @property
    def __dict__(self):
        res = {}
        if self.text_length is not None:
            res['textLength'] = self.text_length
        if self.byte_length is not None:
            res['byteLength'] = self.byte_length
        if self.indexed_progress is not None:
            res['indexedProgress'] = self.indexed_progress
        if self.indexed_status is not None:
            res['indexedStatus'] = self.indexed_status
        if self.create_time is not None:
            res['createTime'] = self.create_time
        if self.last_update_time is not None:
            res['lastUpdateTime'] = self.last_update_time
        if self.keywords:
            res['keywords'] = self.keywords
        if self.indexed_error_msg:
            res['indexedErrorMsg'] = self.indexed_error_msg
        return res


class Rerank:
    def __init__(self,
                 enable: Optional[bool] = None,
                 expect_recall_multiples: Optional[float] = None):
        self.enable = enable
        self.expect_recall_multiples = expect_recall_multiples

    @property
    def __dict__(self):
        res = {}
        if self.enable is not None:
            res['enable'] = self.enable
        if self.expect_recall_multiples:
            res['expectRecallMultiples'] = self.expect_recall_multiples
        return res


class SearchParam:
    def __init__(self,
                 content: str,
                 document_set_name: Optional[List[str]] = None,
                 expand_chunk: Optional[List] = None,
                 rerank: Optional[Rerank] = None,
                 filter: Union[Filter, str] = None,
                 limit: Optional[int] = None,
                 ):
        self.content = content
        self.document_set_name = document_set_name
        self.expand_chunk = expand_chunk
        self.rerank = rerank
        self.filter = filter
        self.limit = limit

    @property
    def __dict__(self):
        res = {"content": self.content}
        if self.document_set_name:
            res["documentSetName"] = self.document_set_name
        options = {}
        if self.expand_chunk:
            options['chunkExpand'] = self.expand_chunk
        if self.rerank:
            options['rerank'] = vars(self.rerank)
        res["options"] = options
        if self.filter:
            res["filter"] = self.filter if isinstance(self.filter, str) else self.filter.cond
        if self.limit:
            res["limit"] = self.limit
        return res


class SearchResultData:
    def __init__(self,
                 text: Optional[str] = None,
                 start_pos: Optional[dict] = None,
                 end_pos: Optional[DocumentSet] = None,
                 pre: Optional[List[str]] = None,
                 next: Optional[List[str]] = None,
                 paragraph_title: Optional[str] = None,
                 all_parent_paragraph_titles: Optional[List[str]] = None,
                 ):
        self.text = text
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.pre = pre
        self.next = next
        self.paragraph_title = paragraph_title
        self.all_parent_paragraph_titles = all_parent_paragraph_titles

    @property
    def __dict__(self):
        res = {
            "text": self.text,
            "startPos": self.start_pos,
            "endPos": self.end_pos,
            "pre": self.pre,
            "next": self.next,
        }
        if self.paragraph_title is not None:
            res['paragraphTitle'] = self.paragraph_title
        if self.all_parent_paragraph_titles is not None:
            res['allParentParagraphTitles'] = self.all_parent_paragraph_titles
        return res


class SearchResult:
    def __init__(self,
                 score: float,
                 data: SearchResultData = None,
                 document_set: DocumentSet = None,
                 ):
        self.score = score
        self.data = data
        self.document_set = document_set

    @property
    def __dict__(self):
        res = {"score": self.score}
        if self.data:
            res["data"] = vars(self.data)
        if self.document_set:
            res["documentSet"] = vars(self.document_set)
        return res

    @staticmethod
    def from_dict(coll_view, data: dict):
        res = SearchResult(score=data.get('score'))
        if 'data' in data:
            d = data.get('data')
            res.data = SearchResultData(
                text=d.get('text'),
                start_pos=d.get('startPos'),
                end_pos=d.get('endPos'),
                pre=d.get('pre'),
                next=d.get('next'),
                paragraph_title=d.get('paragraphTitle'),
                all_parent_paragraph_titles =d.get('allParentParagraphTitles'),
            )
        if 'documentSet' in data:
            ds_dict = data['documentSet']
            ds = DocumentSet(collection_view=coll_view, id=ds_dict['documentSetId'], name=ds_dict['documentSetName'])
            ds.load_fields(ds_dict)
            res.document_set = ds
        return res


class QueryParam:
    def __init__(self,
                 document_set_id: Optional[List[str]] = None,
                 document_set_name: Optional[List[str]] = None,
                 filter: Union[Filter, str] = None,
                 ):
        self.document_set_id = document_set_id
        self.document_set_name = document_set_name
        self.filter = filter

    @property
    def __dict__(self):
        res = {}
        if self.document_set_id:
            res['documentSetId'] = self.document_set_id
        if self.document_set_name:
            res["documentSetName"] = self.document_set_name
        if self.filter:
            res["filter"] = self.filter if isinstance(self.filter, str) else self.filter.cond
        return res
