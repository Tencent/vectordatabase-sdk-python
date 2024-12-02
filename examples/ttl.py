# TTL example
import time

import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams
from numpy import ndarray
import numpy as np


vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-ttl"
coll_name = "sdk_collection_ttl"


# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root')


# create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)


# create Collection
index = Index()
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
index.add(VectorIndex('vector', 32, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex('expire_at', FieldType.Uint64, index_type=IndexType.FILTER))
coll = db.create_collection_if_not_exists(
    name=coll_name,
    shard=1,
    replicas=0,
    description='test collection',
    index=index,
    ttl_config={                                        # use ttl config
        'enable': True,                                 # enable ttl
        'timeField': 'expire_at'                        # doc will expire when the timestamp set by expire_at is reached
    }
)
print(coll.ttl_config)


# upsert docs
vecs: ndarray = np.random.rand(2, 32)
res = coll.upsert(
    documents=[
        {
            'id': '0001',
            'vector': vecs[0],
        },
        {
            'id': '0002',
            'vector': vecs[1],
            # This doc will expire after 10 minutes and be cleared in the next detection cycle, which is 1 hour
            'expire_at': int(time.time()) + 10*60,
        }
    ]
)
print(res, flush=True)


# query
time.sleep(61*60)
res = coll.query(document_ids=['0001', '0002'])
print(res, flush=True)                      # doc(0002) is invalid and will not be searchable after it is cleared


# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
