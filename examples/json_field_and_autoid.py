# json field and auto id example
import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import VectorIndex, FilterIndex, HNSWParams

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-json"
coll_name = "sdk_collection_json"

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
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name,
    shard=1,
    replicas=1,
    description='test collection',
    indexes=[
        FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY, auto_id='uuid'),
        VectorIndex('vector', 1, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)),
        FilterIndex(name='field_json', field_type=FieldType.Json, index_type=IndexType.FILTER),
    ],
)

# print collection
print(vars(vdb_client.collection(database_name=db_name, collection_name=coll_name)))

# upsert test data
res = vdb_client.upsert(
    database_name=db_name,
    collection_name=coll_name,
    documents=[
        {
            'vector': [0],
            'field_json': {
                "username": "Alice",
                "age": 28,
            }
        },
        {
            'vector': [0.1],
            'field_json': {
                "username": "Bob",
                "age": 25,
            }
        },
        {
            'vector': [0.2],
            'field_json': {
                "username": "Charlie",
                "age": 35,
            }
        },
        {
            'vector': [0.3],
            'field_json': {
                'username': 'David',
                'age': 28,
            }
        }
    ]
)

# filter example
print(vdb_client.query(
    database_name=db_name,
    collection_name=coll_name,
    filter='field_json.username="David"',
    limit=10,
))

# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
