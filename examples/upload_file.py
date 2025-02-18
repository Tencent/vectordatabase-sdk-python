# upload file example
import json
import time


import tcvectordb
from tcvectordb.model.collection import Embedding
from tcvectordb.model.collection_view import SplitterProcess, ParsingProcess
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-upload"
coll_name = "sdk_collection_upload"

# tcvectordb.debug.DebugEnable = True

# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root')
# vdb_client.drop_database(db_name)
# create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)
# create Collection with embedding
# ebd = Embedding(vector_field='vector', field='text', model_name='bge-base-zh')
index = Index()
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
index.add(VectorIndex('vector', 768, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex(name='file_name', field_type=FieldType.String, index_type=IndexType.FILTER))
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
    # embedding=ebd,
)

# upload file
vdb_client.upload_file(
    database_name=db_name,
    collection_name=coll_name,
    local_file_path="../tests/files/tcvdb.pdf",
    metadata={
        'teststr': 'v1',
        'testint': 1024,
    },
    splitter_process=SplitterProcess(
        append_keywords_to_chunk=False,
        append_title_to_chunk=True,
        # chunk_splitter='\n\n\n',
    ),
    parsing_process=ParsingProcess(
        parsing_type="AlgorithmParsing",
    ),
    embedding_model='bge-base-zh',
    field_mappings={
        "filename": "file_name",
        "text": "text",
        "imageList": "image_list"
    }
)

# wait for the file parsing to complete.
time.sleep(15)
# query file chunks
res = vdb_client.query(
    database_name=db_name,
    collection_name=coll_name,
    filter='file_name="tcvdb.pdf"',
    limit=100,
)
print(json.dumps(res, ensure_ascii=False))
# get image urls for document
print(vdb_client.get_image_url(database_name=db_name,
                               collection_name=coll_name,
                               document_ids=[res[0].get('id')],
                               file_name='tcvdb.pdf',
                               ))

# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
