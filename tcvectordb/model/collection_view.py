import base64
import json
import os
import urllib
from enum import Enum, unique
from typing import Optional, List, Union, Dict

from qcloud_cos import CosConfig, CosS3Client

from tcvectordb import exceptions
from tcvectordb.debug import Debug, Warning
from tcvectordb.model.document import Filter, Document
from tcvectordb.model.document_set import DocumentSet, SearchParam, QueryParam, \
    Rerank, SearchResult, Chunk
from tcvectordb.model.enum import ReadConsistency
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
                 append_keywords_to_chunk: Optional[bool] = None,
                 chunk_splitter: Optional[str] = None):
        self.append_title_to_chunk = append_title_to_chunk
        self.append_keywords_to_chunk = append_keywords_to_chunk
        self.chunk_splitter = chunk_splitter

    @property
    def __dict__(self):
        res = {}
        if self.append_title_to_chunk is not None:
            res['appendTitleToChunk'] = self.append_title_to_chunk
        if self.append_keywords_to_chunk is not None:
            res['appendKeywordsToChunk'] = self.append_keywords_to_chunk
        if self.chunk_splitter is not None:
            res['chunkSplitter'] = self.chunk_splitter
        return res


class ParsingProcess:
    def __init__(self,
                 parsing_type: Optional[str] = None,
                 **kwargs):
        self.parsing_type = parsing_type
        self.kwargs = kwargs

    @property
    def __dict__(self):
        res = {}
        if self.parsing_type is not None:
            res['parsingType'] = self.parsing_type
        res.update(self.kwargs)
        return res


class CollectionView:
    """The collection view of the document group, composed of multiple DocumentSets."""

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
        self.db = db
        self.name: str = name
        self.description: str = description
        self.embedding: Optional[Embedding] = embedding
        self.splitter_process: Optional[SplitterProcess] = splitter_process
        self.index: Optional[Index] = index
        self.expected_file_num: Optional[int] = expected_file_num
        self.average_file_size: Optional[int] = average_file_size
        self.shard: Optional[int] = shard
        self.replicas: Optional[int] = replicas
        self.parsing_process: Optional[ParsingProcess] = parsing_process
        self.create_time: Optional[str] = None
        self.stats: Optional[dict] = None
        self.alias: Optional[list] = None
        self.conn_name = name

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
        if self.parsing_process:
            res_dict['parsingProcess'] = vars(self.parsing_process)
        if self.index:
            res_dict['indexes'] = self.index.list()
        if self.create_time:
            res_dict['createTime'] = self.create_time
        if self.stats:
            res_dict['stats'] = self.stats
        if self.alias:
            res_dict['alias'] = self.alias
        if self.expected_file_num is not None:
            res_dict['expectedFileNum'] = self.expected_file_num
        if self.average_file_size is not None:
            res_dict['averageFileSize'] = self.average_file_size
        if self.shard is not None:
            res_dict['shardNum'] = self.shard
        if self.replicas is not None:
            res_dict['replicaNum'] = self.replicas
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
        if 'parsingProcess' in fields:
            pp = fields.get('parsingProcess')
            self.parsing_process = ParsingProcess(
                parsing_type=pp.get('parsingType'),
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
        if 'expectedFileNum' in fields:
            self.expected_file_num = fields.get('expectedFileNum')
        if 'averageFileSize' in fields:
            self.average_file_size = fields.get('averageFileSize')
        if 'shardNum' in fields:
            self.shard = fields.get('shardNum')
        if 'replicaNum' in fields:
            self.replicas = fields.get('replicaNum')

    # The following is the document API

    def _check_file_size(self, local_file_path: str, max_length: int):
        file_stat = os.stat(local_file_path)
        if file_stat.st_size == 0:
            raise exceptions.ParamError(
                message='{} 0 bytes file denied'.format(local_file_path))
        if max_length < file_stat.st_size:
            raise exceptions.ParamError(
                message='{} fileSize is invalid, support max content length is {} bytes'.format(
                    local_file_path, max_length))

    def _get_cos_metadata(self,
                          metadata: dict = None,
                          splitter_process: Optional[SplitterProcess] = None,
                          parsing_process: Optional[ParsingProcess] = None):
        cos_metadata = {}
        if not metadata:
            metadata = {}
        for k, v in metadata.items():
            if k.startswith('_'):
                raise exceptions.ParamError(
                    message='field {} can not start with "-"'.format(k))
        cos_metadata['x-cos-meta-data'] = \
            urllib.parse.quote(base64.b64encode(json.dumps(metadata).encode('utf-8')))
        config = {}
        if splitter_process:
            config = vars(splitter_process)
        if parsing_process:
            config['parsingProcess'] = vars(parsing_process)
        cos_metadata['x-cos-meta-config'] = \
            urllib.parse.quote(base64.b64encode(json.dumps(config).encode('utf-8')))
        return cos_metadata

    def _chunk_splitter_check(self,
                              local_file_path: str,
                              splitter_process: Optional[SplitterProcess] = None,
                              parsing_process: Optional[ParsingProcess] = None,
                              ):
        if splitter_process is None or splitter_process.chunk_splitter is None:
            return
        _, extension = os.path.splitext(local_file_path)
        if extension.lower() in {'.pdf', '.pptx'}:
            Warning("The splitter_process.chunk_splitter parameter is valid only for markdown and word files")
        if parsing_process and parsing_process.parsing_type == "VisionModelParsing" \
                and extension.lower() in {'.md', '.markdown'}:
            Warning("parsing_process.parsing_type setting does not take effect, "
                    "Markdown file can only use AlgorithmParsing")

    def load_and_split_text(self,
                            local_file_path: str,
                            document_set_name: Optional[str] = None,
                            metadata: Optional[dict] = None,
                            splitter_process: Optional[SplitterProcess] = None,
                            timeout: Optional[float] = None,
                            parsing_process: Optional[ParsingProcess] = None) -> DocumentSet:
        """Upload local file, parse and save it remotely.

        Args:
            local_file_path  : File path to load
            document_set_name: File name as DocumentSet
            metadata         : Extra properties to save
            splitter_process : Args for splitter process
            timeout          : An optional duration of time in seconds to allow for the request
                               When timeout is set to None, will use the connect timeout
            parsing_process  : Document parsing parameters
        Returns:
            DocumentSet
        """
        # file check
        if not os.path.exists(local_file_path):
            raise exceptions.ParamError(message="file not found: {}".format(local_file_path))
        if not os.path.isfile(local_file_path):
            raise exceptions.ParamError(message="not a file: {}".format(local_file_path))
        # chunk splitter check
        self._chunk_splitter_check(local_file_path, splitter_process)
        # metadata check
        cos_metadata = self._get_cos_metadata(metadata, splitter_process, parsing_process)
        _, file_name = os.path.split(local_file_path)
        if not document_set_name:
            document_set_name = file_name
        # request cos upload accredit
        body = {
            'database': self.db.database_name,
            'collectionView': self.conn_name,
            'documentSetName': document_set_name,
            'byteLength': os.stat(local_file_path).st_size,
        }
        if parsing_process:
            body['parsingProcess'] = vars(parsing_process)
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
        endpoint = cos_endpoint.split('.', 1)[1]
        config = CosConfig(Endpoint=endpoint,
                           SecretId=credentials.get('TmpSecretId'),
                           SecretKey=credentials.get('TmpSecretKey'),
                           Token=credentials.get('Token'))
        client = CosS3Client(config)
        document_set_id = res.body.get('documentSetId')
        cos_metadata['x-cos-meta-id'] = document_set_id
        cos_metadata['x-cos-meta-source'] = 'PythonSDK'
        with open(local_file_path, 'rb') as fp:
            response = client.put_object(
                Bucket=bucket,
                Key=upload_path,
                Body=fp,
                Metadata=cos_metadata
            )
        Debug("Put object response:")
        Debug(response)
        return DocumentSet(
            self,
            id=document_set_id,
            name=document_set_name,
            indexed_progress=0,
            indexed_status='New',
            splitter_process=splitter_process,
            parsing_process=parsing_process,
        )

    def search(self,
               content: str,
               document_set_name: Optional[List[str]] = None,
               expand_chunk: Optional[list] = None,
               rerank: Optional[Rerank] = None,
               filter: Union[Filter, str] = None,
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
            'collectionView': self.conn_name,
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
              filter: Union[Filter, str] = None,
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
            'collectionView': self.conn_name,
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
            query['filter'] = filter if isinstance(filter, str) else filter.cond
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
            ds.load_fields(doc, self._parse_splitter_preprocess(doc), self._parse_parsing_process(doc))
            res.append(ds)
        return res

    def _parse_splitter_preprocess(self, doc: dict):
        if 'splitterPreprocess' not in doc:
            return None
        splitter = doc['splitterPreprocess']
        return SplitterProcess(
            append_title_to_chunk=splitter.get('appendTitleToChunk'),
            append_keywords_to_chunk=splitter.get('appendKeywordsToChunk'),
            chunk_splitter=splitter.get('chunkSplitter'),
        )

    def _parse_parsing_process(self, doc: dict):
        if 'parsingProcess' not in doc:
            return None
        pp = doc['parsingProcess']
        return ParsingProcess(
            parsing_type=pp.get('parsingType'),
        )

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
            "collectionView": self.conn_name,
            "documentSetName": document_set_name,
            "documentSetId": document_set_id,
        }
        res = self.db.conn.post('/ai/documentSet/get', body, timeout)
        data = res.body.get('documentSet')
        if not data:
            return None
        ds = DocumentSet(self, id=data['documentSetId'], name=data['documentSetName'])
        ds.load_fields(data, self._parse_splitter_preprocess(data), self._parse_parsing_process(data))
        return ds

    def delete(self,
               document_set_id: Union[str, List[str]] = None,
               document_set_name: Union[str, List[str]] = None,
               filter: Union[Filter, str] = None,
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
            "collectionView": self.conn_name,
            "query": vars(query),
        }
        res = self.db.conn.post('/ai/documentSet/delete', body, timeout)
        return res.data()

    def update(self,
               data: Document,
               document_set_id: Union[str, List[str]] = None,
               document_set_name: Union[str, List[str]] = None,
               filter: Union[Filter, str] = None,
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
            "collectionView": self.conn_name,
            "query": vars(query),
            "update": vars(data)
        }
        res = self.db.conn.post('/ai/documentSet/update', body, timeout)
        return res.data()

    def get_chunks(self,
                   document_set_id: Optional[str] = None,
                   document_set_name: Optional[str] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None,
                   timeout: Optional[float] = None,
                   ) -> List[Chunk]:
        """Get chunks of document set.

        Args:
            document_set_id  : DocumentSet's id
            document_set_name: DocumentSet's name
            limit            : The limit of the result
            offset           : The offset of the result
            timeout          : An optional duration of time in seconds to allow for the request
                               When timeout is set to None, will use the connect timeout
        Returns:
            List[Chunk]
        """
        if (not document_set_id) and (not document_set_name):
            raise exceptions.ParamError(message="please provide document_set_id or document_set_name")
        body = {
            'database': self.db.database_name,
            'collectionView': self.conn_name,
        }
        if document_set_id is not None:
            body['documentSetId'] = document_set_id
        if document_set_name is not None:
            body['documentSetName'] = document_set_name
        if limit is not None:
            body['limit'] = limit
        if offset is not None:
            body['offset'] = offset
        res = self.db.conn.post('/ai/documentSet/getChunks', body, timeout)
        chunks = res.body.get('chunks', [])
        res = []
        if not chunks:
            return []
        for ck in chunks:
            chunk = Chunk(start_pos=ck.get('startPos'),
                          end_pos=ck.get('endPos'),
                          text=ck.get('text'),
                          )
            res.append(chunk)
        return res

    def upload_file(self,
                    local_file_path: str,
                    file_name: Optional[str] = None,
                    splitter_process: Optional[SplitterProcess] = None,
                    parsing_process: Optional[ParsingProcess] = None,
                    embedding_model: Optional[str] = None,
                    field_mappings: Optional[Dict[str, str]] = None,
                    metadata: Optional[dict] = None,
                    ) -> dict:
        """Upload file to a Base Database.

        Args:
            local_file_path (str): File path to load
            file_name (str): File name as DocumentSet
            splitter_process (SplitterProcess): Args for splitter process
            parsing_process (ParsingProcess): Document parsing parameters
            embedding_model (str): embedding model
            metadata (Dict): Extra properties to save
            field_mappings (Dict): Field mappings for Collection to save. filename must be a filter index
                For example: {"filename": "file_name", "text": "text", "imageList": "image_list"}

        Returns:
            dict
        """
        # file check
        if not os.path.exists(local_file_path):
            raise exceptions.ParamError(message="file not found: {}".format(local_file_path))
        if not os.path.isfile(local_file_path):
            raise exceptions.ParamError(message="not a file: {}".format(local_file_path))
        # chunk splitter check
        self._chunk_splitter_check(local_file_path, splitter_process)
        # metadata check
        cos_metadata = self._get_cos_metadata(metadata=metadata)
        _, f_name = os.path.split(local_file_path)
        if not file_name:
            file_name = f_name
        # request cos upload accredit
        body = {
            'database': self.db.database_name,
            'collection': self.conn_name,
            'fileName': file_name,
            'byteLength': os.stat(local_file_path).st_size,
        }
        if splitter_process:
            body['splitterPreprocess'] = vars(splitter_process)
        if parsing_process:
            body['parsingProcess'] = vars(parsing_process)
        if embedding_model:
            body['embeddingModel'] = embedding_model
        if field_mappings:
            body['fieldMappings'] = field_mappings
        res = self.db.conn.post('/ai/document/uploadUrl', body)
        upload_condition = res.body.get('uploadCondition')
        credentials = res.body.get('credentials')
        if not upload_condition or not credentials:
            raise exceptions.ParamError(message="get file upload url failed")
        self._check_file_size(local_file_path, upload_condition.get('maxSupportContentLength', 0))
        warning = res.body.get('warning')
        if warning:
            Warning(warning)
        # upload to cos
        upload_path = res.body.get('uploadPath')
        cos_endpoint = res.body.get('cosEndpoint')
        bucket = cos_endpoint.split('.')[0].replace('https://', '').replace('http://', '')
        endpoint = cos_endpoint.split('.', 1)[1]
        config = CosConfig(Endpoint=endpoint,
                           SecretId=credentials.get('TmpSecretId'),
                           SecretKey=credentials.get('TmpSecretKey'),
                           Token=credentials.get('Token'))
        client = CosS3Client(config)
        cos_metadata['x-cos-meta-source'] = 'PythonSDK'
        with open(local_file_path, 'rb') as fp:
            response = client.put_object(
                Bucket=bucket,
                Key=upload_path,
                Body=fp,
                Metadata=cos_metadata
            )
        Debug("Put cos object response:")
        Debug(response)
        body['id'] = file_name
        return body

    def get_image_url(self,
                      document_ids: List[str],
                      file_name: str) -> List[List[dict]]:
        """Get image urls for document.

        Args:
            document_ids (List[str]): Document ids
            file_name (str): file name
        Returns:
            List[List[dict]]:
        """
        body = {
            'database': self.db.database_name,
            'collection': self.conn_name,
            'documentIds': document_ids,
            'fileName': file_name,
        }
        res = self.db.conn.post('/ai/document/getImageUrl', body)
        return res.data().get('images', [])

    def query_file_details(self,
                           database_name: str,
                           collection_name: str,
                           file_names: List[str] = None,
                           filter: Union[Filter, str] = None,
                           output_fields: Optional[List[str]] = None,
                           limit: Optional[int] = None,
                           offset: Optional[int] = None,
                           read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                           ) -> List[Dict]:
        """Query documents that satisfies the condition.

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            file_names (List[str]): The list of the filename
            filter (Union[Filter, str]): Filter condition of the scalar index field
            output_fields (List[str]): document's fields to return
            limit (int): All ids of the document to be queried
            offset (int): Page offset, used to control the starting position of the results
            read_consistency: (ReadConsistency): Control the consistency level for read operations.

        Returns:
            List[Dict]: all matched documents
        """
        query = {}
        if file_names is not None:
            query['fileNames'] = file_names
        if filter is not None:
            query['filter'] = filter if isinstance(filter, str) else filter.cond
        if limit is not None:
            query['limit'] = limit
        if offset is not None:
            query['offset'] = offset
        if output_fields:
            query['outputFields'] = output_fields
        body = {
            'database': database_name,
            'collection': collection_name,
            'query': query,
            'readConsistency': read_consistency.value
        }
        res = self.db.conn.post('/ai/document/queryFileDetails', body)
        documents = res.body.get('documents', None)
        res = []
        if not documents:
            return []
        for doc in documents:
            res.append(doc)
        return res
