# hnsw quantization
import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-quantization"
coll_name_vector = "sdk_collection"
coll_name_binary_vector = "sdk_collection_binary"
coll_name_float16_vector = "sdk_collection_float16"
coll_name_bfloat16_vector = "sdk_collection_bfloat16"

tcvectordb.debug.DebugEnable = False


# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root',
                                          )
# vdb_client.drop_database(db_name)
# create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)
# create Vector Collection
index = Index()
index.add(FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY))
index.add(VectorIndex('vector', 32, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex(name='username', field_type=FieldType.String, index_type=IndexType.FILTER))
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name_vector,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
)
coll = vdb_client.describe_collection(database_name=db_name, collection_name=coll_name_vector)
print(vars(coll))

# create BinaryVector Collection
index = Index()
index.add(FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY))
index.add(VectorIndex(name='vector',
                      field_type=FieldType.BinaryVector,
                      dimension=32,
                      index_type=IndexType.BIN_FLAT,
                      metric_type=MetricType.HAMMING,
                      params=HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex(name='username', field_type=FieldType.String, index_type=IndexType.FILTER))
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name_binary_vector,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
)
coll = vdb_client.describe_collection(database_name=db_name, collection_name=coll_name_binary_vector)
print(vars(coll))

# create Float16Vector Collection
index = Index()
index.add(FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY))
index.add(VectorIndex(name='vector',
                      field_type=FieldType.Float16Vector,
                      dimension=32,
                      index_type=IndexType.HNSW,
                      metric_type=MetricType.IP,
                      params=HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex(name='username', field_type=FieldType.String, index_type=IndexType.FILTER))
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name_float16_vector,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
)
coll = vdb_client.describe_collection(database_name=db_name, collection_name=coll_name_float16_vector)
print(vars(coll))

# create BFloat16Vector Collection
index = Index()
index.add(FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY))
index.add(VectorIndex(name='vector',
                      field_type=FieldType.BFloat16Vector,
                      dimension=32,
                      index_type=IndexType.HNSW,
                      metric_type=MetricType.IP,
                      params=HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex(name='username', field_type=FieldType.String, index_type=IndexType.FILTER))
coll = vdb_client.create_collection_if_not_exists(
    database_name=db_name,
    collection_name=coll_name_bfloat16_vector,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
)
coll = vdb_client.describe_collection(database_name=db_name, collection_name=coll_name_bfloat16_vector)
print(vars(coll))

vdb_client.modify_vector_index(database_name=db_name,
                               collection_name=coll_name_bfloat16_vector,
                               vector_indexes=[
                                   VectorIndex(
                                       metric_type=MetricType.COSINE,
                                       params={
                                           "M": 32,
                                           "efConstruction": 400
                                       },
                                   ),
                               ],
                               rebuild_rules={
                                   "throttle": 1
                               })
coll = vdb_client.describe_collection(database_name=db_name, collection_name=coll_name_bfloat16_vector)
print(vars(coll))

# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
