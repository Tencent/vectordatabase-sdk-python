# count and delete limit example
import time
import numpy as np

import tcvectordb
from tcvectordb.model.document import Filter
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams


vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-count"
coll_name = "sdk_collection_count"

tcvectordb.debug.DebugEnable = False


# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root',
                                          )
# vdb_client.drop_database(db_name)
# create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)
# create Collection
index = Index()
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
index.add(VectorIndex('vector', 32, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex(name='username', field_type=FieldType.String, index_type=IndexType.FILTER))
index.add(FilterIndex(name='age', field_type=FieldType.Uint64, index_type=IndexType.FILTER))
coll = db.create_collection_if_not_exists(
    name=coll_name,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
)
# upsert test data
vecs: list = np.random.rand(4, 32).tolist()
res = vdb_client.upsert(
    database_name=db_name,
    collection_name=coll_name,
    documents=[
        {
            'id': '0001',
            'vector': vecs[0],
            'username': 'Alice',
            'age': 28,
        },
        {
            'id': '0002',
            'vector': vecs[1],
            'username': 'Bob',
            'age': 25,
        },
        {
            'id': '0003',
            'vector': vecs[2],
            'username': 'Charlie',
            'age': 35,
        },
        {
            'id': '0004',
            'vector': vecs[3],
            'username': 'David',
            'age': 28,
        }
    ]
)
time.sleep(5)
print(vars(db.collection(coll_name)))


# count example
doc_count = vdb_client.count(database_name=db_name, collection_name=coll_name, filter=Filter('age<28'))
print(doc_count, doc_count == 2)

# delete limit example
print(vdb_client.delete(database_name=db_name,
                        collection_name=coll_name,
                        filter=Filter('age=28'),
                        limit=1))
time.sleep(1)
doc_count = vdb_client.count(database_name=db_name, collection_name=coll_name, filter=Filter('age=28'))
print(doc_count)
print(vdb_client.delete(database_name=db_name,
                        collection_name=coll_name,
                        filter=Filter('age=28'),
                        limit=0))
time.sleep(1)
doc_count = vdb_client.count(database_name=db_name, collection_name=coll_name, filter=Filter('age=28'))


# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
