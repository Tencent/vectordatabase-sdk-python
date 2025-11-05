# IVF_RABITQ and uint64 double example
import time

import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, IVFRABITQParams
import numpy as np

tcvectordb.debug.DebugEnable = False


vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-rabitq"
coll_name = "sdk_collection_rabitq"


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
index.add(VectorIndex(name='vector',
                      dimension=64,
                      index_type=IndexType.IVF_RABITQ,
                      metric_type=MetricType.IP,
                      params=IVFRABITQParams(nlist=1, bits=1)))
index.add(FilterIndex('profit', FieldType.Int64, index_type=IndexType.FILTER))
index.add(FilterIndex('percent', FieldType.Double, index_type=IndexType.FILTER))
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name,
    shard=1,
    replicas=0,
    description='test collection',
    index=index,
)
print(vars(vdb_client.collection(database_name=db_name, collection_name=coll_name)))


# upsert docs
vecs = np.random.rand(64, 64).tolist()
for i in range(64):
    res = vdb_client.upsert(
        database_name=db_name,
        collection_name=coll_name,
        documents=[
            {
                'id': str(i),
                'vector': vecs[i],
                'profit': i * -1,
                'percent': 1/(i+1),
            }
        ],
        build_index=False,
    )
vdb_client.rebuild_index(database_name=db_name, collection_name=coll_name)
time.sleep(2)

# query
print(vdb_client.query(database_name=db_name,
                       collection_name=coll_name,
                       limit=2
                       ))

# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
