import base64
import json
import os
import urllib
from enum import Enum, unique
from typing import Optional, List, Union

from qcloud_cos import CosConfig, CosS3Client

from tcvectordb import exceptions
from tcvectordb.debug import Debug
from tcvectordb.model.document import Filter, Document
from tcvectordb.model.document_set import FileType, DocumentSet, SearchParam, QueryParam, \
    Rerank, SearchResult
from tcvectordb.model.index import Index


@unique
class Language(Enum):
    ZH = "zh"
    EN = "en"
    MULTI = "multi"


class Embedding:
    def __init__(self,
                 language: Optional[str] = None,
                 enable_words_embedding: Optional[bool] = None):
        self.language = language
        self.enable_words_embedding = enable_words_embedding

    @property
    def __dict__(self):
        res = {}
        if self.language:
            res['language'] = self.language
        if self.enable_words_embedding is not None:
            res['enableWordsEmbedding'] = self.enable_words_embedding
        return res


class SplitterProcess:
    def __init__(self,
                 append_title_to_chunk: Optional[bool] = None,
                 append_keywords_to_chunk: Optional[bool] = None):
        self.append_title_to_chunk = append_title_to_chunk
        self.append_keywords_to_chunk = append_keywords_to_chunk

    @property
    def __dict__(self):
        res = {}
        if self.append_title_to_chunk is not None:
            res['appendTitleToChunk'] = self.append_title_to_chunk
        if self.append_keywords_to_chunk is not None:
            res['appendKeywordsToChunk'] = self.append_keywords_to_chunk
        return res


class CollectionView:
    """CollectionView and about DocumentSet operating."""

    def __init__(self,
                 db,
                 name: str,
                 description: str = '',
                 embedding: Optional[Embedding] = None,
                 splitter_process: Optional[SplitterProcess] = None,
                 index: Optional[Index] = None,
                 ):
        self.db = db
        self.name: str = name
        self.description: str = description
        self.embedding: Optional[Embedding] = embedding
        self.splitter_process: Optional[SplitterProcess] = splitter_process
        self.index: Optional[Index] = index
        self.create_time: Optional[str] = None
        self.stats: Optional[dict] = None
        self.alias: Optional[list] = None

    @property
    def __dict__(self):
        res_dict = {
            'database': self.db.database_name,
            'collectionView': self.name,
        }
        if self.description:
            res_dict['description'] = self.description
        if self.embedding:
            res_dict['embedding'] = vars(self.embedding)
        if self.splitter_process:
            res_dict['splitterPreprocess'] = vars(self.splitter_process)
        if self.index:
            res_dict['indexes'] = self.index.list()
        if self.create_time:
            res_dict['createTime'] = self.create_time
        if self.stats:
            res_dict['stats'] = self.stats
        if self.alias:
            res_dict['alias'] = self.alias
        return res_dict

    def load_fields(self, fields: dict):
        if 'description' in fields:
            self.description = fields.get('description')
        if 'embedding' in fields:
            emb = fields.get('embedding')
            self.embedding = Embedding(
                language=emb.get('language'),
                enable_words_embedding=emb.get('enableWordsEmbedding')
            )
        if 'splitterPreprocess' in fields:
            spl = fields.get('splitterPreprocess')
            self.splitter_process = SplitterProcess(
                append_title_to_chunk=spl.get('appendTitleToChunk'),
                append_keywords_to_chunk=spl.get('appendKeywordsToChunk')
            )
        self.index = Index()
        for elem in fields.get('indexes', []):
            self.index.add(**elem)
        if 'createTime' in fields:
            self.create_time = fields.get('createTime')
        if 'stats' in fields:
            self.stats = fields.get('stats')
        if 'alias' in fields:
            self.alias = fields.get('alias')

    # The following is the document API

    def _parse_file_type(self, local_file_path: str):
        _, extension = os.path.splitext(local_file_path)
        if extension == "":
            return FileType.Markdown
        elif extension == ".md":
            return FileType.Markdown
        elif extension == ".markdown":
            return FileType.Markdown
        else:
            return FileType.UnSupport

    def _check_file_size(self, local_file_path: str, max_length: int):
        file_stat = os.stat(local_file_path)
        if file_stat.st_size == 0:
            raise exceptions.ParamError(
                message='{} 0 bytes file denied'.format(local_file_path))
        if max_length < file_stat.st_size:
            raise exceptions.ParamError(
                message='{} fileSize is invalid, support max content length is {} bytes'.format(
                    local_file_path, max_length))

    def _get_cos_metadata(self, metadata: dict = None):
        cos_metadata = {}
        if not metadata:
            metadata = {}
        for k, v in metadata.items():
            if k.startswith('_'):
                raise exceptions.ParamError(
                    message='field {} can not start with "-"'.format(k))
        cos_metadata['x-cos-meta-data'] = \
            urllib.parse.quote(base64.b64encode(json.dumps(metadata).encode('utf-8')))
        return cos_metadata

    def load_and_split_text(self,
                            local_file_path: str,
                            document_set_name: Optional[str] = None,
                            metadata: Optional[dict] = None,
                            timeout: Optional[float] = None) -> DocumentSet:
        """Upload local file, parse and save it remotely.

        Args:
            local_file_path  : File path to load
            document_set_name: File name as DocumentSet
            metadata         : Extra properties to save
            timeout          : An optional duration of time in seconds to allow for the request
                               When timeout is set to None, will use the connect timeout
        Returns:
            DocumentSet
        """
        # file check
        if not os.path.exists(local_file_path):
            raise exceptions.ParamError(message="file not found: {}".format(local_file_path))
        if not os.path.isfile(local_file_path):
            raise exceptions.ParamError(message="not a file: {}".format(local_file_path))
        # metadata check
        cos_metadata = self._get_cos_metadata(metadata)
        # parse file type
        file_type = self._parse_file_type(local_file_path)
        if FileType.UnSupport == file_type:
            raise exceptions.ParamError(message="only markdown file can upload")
        _, file_name = os.path.split(local_file_path)
        if not document_set_name:
            document_set_name = file_name
        # request cos upload accredit
        body = {
            'database': self.db.database_name,
            'collectionView': self.name,
            'documentSetName': document_set_name,
        }
        res = self.db.conn.post('/ai/documentSet/uploadUrl', body, timeout)
        upload_condition = res.body.get('uploadCondition')
        credentials = res.body.get('credentials')
        if not upload_condition or not credentials:
            raise exceptions.ParamError(message="get file upload url failed")
        self._check_file_size(local_file_path, upload_condition.get('maxSupportContentLength', 0))
        # upload to cos
        upload_path = res.body.get('uploadPath')
        cos_endpoint = res.body.get('cosEndpoint')
        bucket = cos_endpoint.split('.')[0].replace('https://', '').replace('http://', '')
        region = cos_endpoint.split('.')[2]
        config = CosConfig(Region=region,
                           SecretId=credentials.get('TmpSecretId'),
                           SecretKey=credentials.get('TmpSecretKey'),
                           Token=credentials.get('Token'))
        client = CosS3Client(config)
        document_set_id = res.body.get('documentSetId')
        cos_metadata['x-cos-meta-id'] = document_set_id
        cos_metadata['x-cos-meta-source'] = 'PythonSDK'
        response = client.upload_file(
            Bucket=bucket,
            Key=upload_path,
            LocalFilePath=local_file_path,
            Metadata=cos_metadata
        )
        Debug(json.dumps(response, indent=2))
        return DocumentSet(
            self,
            id=document_set_id,
            name=document_set_name,
            indexed_progress=0,
            indexed_status='New',
        )

    def search(self,
               content: str,
               document_set_name: Optional[List[str]] = None,
               expand_chunk: Optional[list] = None,
               rerank: Optional[Rerank] = None,
               filter: Optional[Filter] = None,
               limit: Optional[int] = None,
               timeout: Optional[float] = None,
               ) -> List[SearchResult]:
        """Search document.

        Args:
            content          : The content to apply similarity search
            document_set_name: DocumentSet's name
            expand_chunk     : Parameters for Forward and Backward Expansion of Chunks
            rerank           : Parameters for Rerank
            filter           : The optional filter condition of the scalar index field
            limit            : The limit of the query result, not support now
            timeout          : An optional duration of time in seconds to allow for the request.
                               When timeout is set to None, will use the connect timeout.
        Returns:
            doc list
        """
        search_param = SearchParam(
            content=content,
            document_set_name=document_set_name,
            expand_chunk=expand_chunk,
            rerank=rerank,
            filter=filter,
            limit=limit,
        )
        body = {
            'database': self.db.database_name,
            'collectionView': self.name,
            'search': vars(search_param)
        }
        res = self.db.conn.post('/ai/documentSet/search', body, timeout)
        documents = res.body.get('documents', [])
        res = []
        if not documents:
            return []
        for doc in documents:
            res.append(SearchResult.from_dict(self, doc))
        return res

    def query(self,
              document_set_id: Optional[List] = None,
              document_set_name: Optional[List[str]] = None,
              filter: Optional[Filter] = None,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              output_fields: Optional[List[str]] = None,
              timeout: Optional[float] = None,
              ) -> List[DocumentSet]:
        """Query document set.

        Args:
            document_set_id  : DocumentSet's id to query
            document_set_name: DocumentSet's name to query
            filter           : The optional filter condition of the scalar index field.
            limit            : The limit of the query result
            offset           : The offset of the query result
            output_fields    : The fields to return when query
            timeout          : An optional duration of time in seconds to allow for the request
                               When timeout is set to None, will use the connect timeout
        Returns:
            List[DocumentSet]
        """
        body = {
            'database': self.db.database_name,
            'collectionView': self.name,
        }
        query = {}
        if document_set_id is not None:
            query['documentSetId'] = document_set_id
        if document_set_name is not None:
            query['documentSetName'] = document_set_name
        if limit is not None:
            query['limit'] = limit
        if offset is not None:
            query['offset'] = offset
        if filter is not None:
            query['filter'] = vars(filter)
        if output_fields:
            query['outputFields'] = output_fields
        body['query'] = query
        res = self.db.conn.post('/ai/documentSet/query', body, timeout)
        documents = res.body.get('documentSets', [])
        res = []
        if not documents:
            return []
        for doc in documents:
            ds = DocumentSet(self, id=doc['documentSetId'], name=doc['documentSetName'])
            ds.load_fields(doc)
            res.append(ds)
        return res

    def get_document_set(self,
                         document_set_id: Optional[str] = None,
                         document_set_name: Optional[str] = None,
                         timeout: Optional[float] = None,) -> Union[DocumentSet, None]:
        """Get a document set by document_set_id or document_set_name.

        Args:
            document_set_id  : DocumentSet's id to get
            document_set_name: DocumentSet's name to get
            timeout          : An optional duration of time in seconds to allow for the request
                               When timeout is set to None, will use the connect timeout
        Returns:
            DocumentSet
        """
        if document_set_id is None and document_set_name is None:
            raise exceptions.ParamError(message="please provide document_set_id or document_set_name")
        body = {
            "database": self.db.database_name,
            "collectionView": self.name,
            "documentSetName": document_set_name,
            "documentSetId": document_set_id,
        }
        res = self.db.conn.post('/ai/documentSet/get', body, timeout)
        data = res.body.get('documentSet')
        if not data:
            return None
        ds = DocumentSet(self, id=data['documentSetId'], name=data['documentSetName'])
        ds.load_fields(data)
        return ds

    def delete(self,
               document_set_id: Union[str, List[str]] = None,
               document_set_name: Union[str, List[str]] = None,
               filter: Filter = None,
               timeout: float = None,
               ):
        """Get a document set by document_set_id or document_set_name.

        Args:
            document_set_id  : DocumentSet's id to delete
            document_set_name: DocumentSet's name to delete
            filter           : The optional filter condition of the scalar index field.
            timeout          : An optional duration of time in seconds to allow for the request
                               When timeout is set to None, will use the connect timeout
        Returns:
            affectedCount: affected count in dict
        """
        if (not document_set_id) and (not document_set_name) and filter is None:
            raise exceptions.ParamError(message="please provide document_set_id or document_set_name or filter")
        if document_set_id is not None and isinstance(document_set_id, str):
            document_set_id = [document_set_id]
        if document_set_name is not None and isinstance(document_set_name, str):
            document_set_name = [document_set_name]
        query = QueryParam(document_set_id=document_set_id, document_set_name=document_set_name, filter=filter)
        body = {
            "database": self.db.database_name,
            "collectionView": self.name,
            "query": vars(query),
        }
        res = self.db.conn.post('/ai/documentSet/delete', body, timeout)
        return res.data()

    def update(self,
               data: Document,
               document_set_id: Union[str, List[str]] = None,
               document_set_name: Union[str, List[str]] = None,
               filter: Filter = None,
               timeout: float = None,
               ):
        """Update a document set.

        Args:
            data             : Fields to update
            document_set_id  : DocumentSet's id to update
            document_set_name: DocumentSet's name to update
            filter           : The optional filter condition of the scalar index field.
            timeout          : An optional duration of time in seconds to allow for the request
                               When timeout is set to None, will use the connect timeout
        Returns:
            affectedCount: affected count in dict
        """
        if data is None:
            raise exceptions.ParamError(message='please provide update data')
        if (not document_set_id) and (not document_set_name) and filter is None:
            raise exceptions.ParamError(message="please provide document_set_id or document_set_name or filter")
        if document_set_id is not None and isinstance(document_set_id, str):
            document_set_id = [document_set_id]
        if document_set_name is not None and isinstance(document_set_name, str):
            document_set_name = [document_set_name]
        query = QueryParam(document_set_id=document_set_id, document_set_name=document_set_name, filter=filter)
        body = {
            "database": self.db.database_name,
            "collectionView": self.name,
            "query": vars(query),
            "update": vars(data)
        }
        res = self.db.conn.post('/ai/documentSet/update', body, timeout)
        return res.data()
