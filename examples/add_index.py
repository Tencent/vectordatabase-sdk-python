# add_index example
import time
import numpy as np

import tcvectordb
from tcvectordb.model.document import Filter
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams


vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-add-index"
coll_name = "sdk_collection_add_index"


# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root')
# vdb_client.drop_database(db_name)
# create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)
# create Collection
index = Index()
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
index.add(VectorIndex('vector', 32, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))
coll = db.create_collection_if_not_exists(
    name=coll_name,
    shard=1,
    replicas=0,
    description='test collection',
    index=index,
)
# upsert docs
vecs: list = np.random.rand(4, 32).tolist()
res = coll.upsert(
    documents=[
        {
            'id': '0001',
            'vector': vecs[0],
            'username': 'Alice',
            'age': 30,
            'interest': ['Football', 'Basketball'],
        },
        {
            'id': '0002',
            'vector': vecs[1],
            'username': 'Bob',
            'age': 25,
            'interest': ['Basketball', 'Tennis'],
        },
        {
            'id': '0003',
            'vector': vecs[2],
            'username': 'Charlie',
            'age': 35,
            'interest': ['Tennis', 'Swimming'],
        },
        {
            'id': '0004',
            'vector': vecs[3],
            'username': 'David',
            'age': 28,
            'interest': ['Swimming', 'Running'],
        }
    ]
)
print(res, flush=True)
time.sleep(2)

# add_index
print(vdb_client.add_index(database_name=db_name,
                           collection_name=coll_name,
                           indexes=[
                               FilterIndex(name='username', field_type=FieldType.String, index_type=IndexType.FILTER),
                               FilterIndex(name='age', field_type=FieldType.Uint64, index_type=IndexType.FILTER),
                               FilterIndex(name='interest', field_type=FieldType.Array, index_type=IndexType.FILTER),
                           ],
                           build_existed_data=True),
      )
# Wait for the index build to complete
while True:
    coll = db.describe_collection(coll_name)
    if coll.index_status.get('status') == 'ready':
        print(vars(coll))
        break
    time.sleep(2)
# Use the new index to filter
res = coll.query(filter='username="Bob"', limit=10)
print(res, flush=True)
res = coll.query(filter='age>30', limit=10)
print(res, flush=True)
res = coll.query(filter=Filter(Filter.Include('interest', ['Swimming'])), limit=10)
print(res, flush=True)


# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
