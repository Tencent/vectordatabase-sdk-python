# order by example
import time
import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-order"
coll_name = "sdk_collection_order"

# tcvectordb.debug.DebugEnable = True


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
index.add(VectorIndex('vector', 1, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex(name='username', field_type=FieldType.String, index_type=IndexType.FILTER))
index.add(FilterIndex(name='age', field_type=FieldType.Uint64, index_type=IndexType.FILTER))
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
)
# upsert test data
res = vdb_client.upsert(
    database_name=db_name,
    collection_name=coll_name,
    documents=[
        {
            'id': '0001',
            'vector': [0],
            'username': 'Alice',
            'age': 28,
        },
        {
            'id': '0002',
            'vector': [0],
            'username': 'Bob',
            'age': 25,
        },
        {
            'id': '0003',
            'vector': [0],
            'username': 'Charlie',
            'age': 35,
        },
        {
            'id': '0004',
            'vector': [0],
            'username': 'David',
            'age': 28,
        }
    ]
)
time.sleep(1)

# order example
print(vdb_client.query(
    database_name=db_name,
    collection_name=coll_name,
    sort={
        'fieldName': 'age',
        'direction': 'desc',
    },
    limit=10,
))

# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
