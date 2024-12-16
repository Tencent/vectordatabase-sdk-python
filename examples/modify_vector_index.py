# modify_vector_index example
import time
import numpy as np

import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams


vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-modify-index"
coll_name = "sdk_collection_modify_index"

tcvectordb.debug.DebugEnable = False


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
    shard=2,
    replicas=1,
    description='test collection',
    index=index,
)
# upsert test data
vecs: list = np.random.rand(4, 32).tolist()
res = coll.upsert(
    documents=[
        {
            'id': '0001',
            'vector': vecs[0],
            'username': 'Alice',
        },
        {
            'id': '0002',
            'vector': vecs[1],
            'username': 'Bob',
        },
        {
            'id': '0003',
            'vector': vecs[2],
            'username': 'Charlie',
        },
        {
            'id': '0004',
            'vector': vecs[3],
            'username': 'David',
        }
    ]
)
print(res, flush=True)
time.sleep(2)

# modify vector index
print(vdb_client.modify_vector_index(database_name=db_name,
                                     collection_name=coll_name,
                                     vector_indexes=[
                                         VectorIndex(
                                             metric_type=MetricType.COSINE,
                                             params={
                                                 "M": 8,
                                                 "efConstruction": 0
                                             },
                                         ),
                                     ],
                                     rebuild_rules={
                                         "throttle": 1
                                     }))
time.sleep(2)

# describe collection
coll = db.describe_collection(coll_name)
print(vars(coll))


# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
