# group by example
import json
import numpy as np
import tcvectordb
from tcvectordb.model.document import Document, SearchParams
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import VectorIndex, FilterIndex, HNSWParams
import time

tcvectordb.debug.DebugEnable = False

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-aggregate"
coll_name = "sdk_collection_aggregate"

# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root',
                                          )
# # vdb_client.drop_database(db_name)
# # create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)
# # create Collection
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name,
    shard=1,
    replicas=1,
    description='test collection',
    indexes=[
        VectorIndex('vector', 64, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)),
        FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY),
        FilterIndex('page', FieldType.Uint64, IndexType.FILTER, enable_value_cache=True),
    ],
)

# # upsert test data
vecs: list = np.random.rand(101, 64).tolist()
for i in range(100):
    res = vdb_client.upsert(
        database_name=db_name,
        collection_name=coll_name,
        documents=[
            Document(id='000{}'.format(i),
                     vector=vecs[i],
                     page=i % 10)
        ]
    )
time.sleep(2)
vdb_client.add_index(database_name=db_name,
                     collection_name=coll_name,
                     indexes=[
                         FilterIndex('page1', FieldType.Uint64, IndexType.FILTER, enable_value_cache=True)
                     ])
print(vars(vdb_client.describe_collection(database_name=db_name, collection_name=coll_name)))

# filter example
res = vdb_client.search(
    database_name=db_name,
    collection_name=coll_name,
    vectors=[vecs[100]],
    aggregate={
        "groupBy": "page",
        # "metrics": ["COUNT(*)"],
        "candidateLimit": 2,
    },
    params=SearchParams(ef=200),
    limit=5
)
print(json.dumps(res, indent=2))

# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
