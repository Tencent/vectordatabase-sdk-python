# binary vector example
import time

import tcvectordb
from tcvectordb.model.collection import FilterIndexConfig
from tcvectordb.model.document import Document
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex
from tcvectordb.toolkit.binary import binary_to_uint8

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-binary"
coll_name = "sdk_collection_binary"

tcvectordb.debug.DebugEnable = False

# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root')
# vdb_client.drop_database(db_name)
# create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)
# create Collection with BinaryVector
index = Index()
index.add(VectorIndex('vector',
                      16,
                      IndexType.BIN_FLAT,
                      MetricType.HAMMING,
                      field_type=FieldType.BinaryVector,
                      ))
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
coll = db.create_collection_if_not_exists(
    name=coll_name,
    shard=2,
    replicas=1,
    description='test collection',
    index=index,
    filter_index_config=FilterIndexConfig(
        filter_all=True,
        fields_without_index=['author'],
        max_str_len=32,
    )
)

# upsert binary vectors
res = vdb_client.upsert(
    database_name=db_name,
    collection_name=coll_name,
    documents=[
            Document(id='0001',
                     vector=binary_to_uint8([1, 1, 1, 0, 0, 1, 0, 1,  0, 0, 0, 0, 0, 0, 0, 0]),
                     bookName='西游记',
                     author='吴承恩',
                     page=21),
            Document(id='0002',
                     vector=binary_to_uint8([1, 1, 0, 0, 1, 0, 1, 1,  0, 0, 0, 0, 0, 0, 0, 0]),
                     bookName='西游记',
                     author='吴承恩',
                     page=22),
            Document(id='0003',
                     vector=binary_to_uint8([0, 0, 0, 1, 0, 0, 0, 0,  1, 1, 0, 1, 0, 0, 1, 0]),
                     bookName='三国演义',
                     author='罗贯中',
                     page=23),
            Document(id='0004',
                     vector=binary_to_uint8([0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 1, 0, 0, 1, 0, 0]),
                     bookName='三国演义',
                     author='罗贯中',
                     page=24),
            Document(id='0005',
                     vector=binary_to_uint8([0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 0, 1, 1, 0, 0, 1]),
                     bookName='三国演义',
                     author='罗贯中',
                     page=25),
    ]
)
print(res, flush=True)
time.sleep(2)


# search with binary vector
res = vdb_client.search(
    database_name=db_name,
    collection_name=coll_name,
    vectors=[binary_to_uint8([0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 0, 1, 1, 1, 0, 1])],
    limit=1,
)
print(res)


# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
