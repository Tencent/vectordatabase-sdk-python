# 接口使用示例，包含：exists_db、create_database_if_not_exists、exists_collection、create_collection_if_not_exists
import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams


vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-exists-api"
coll_name = "sdk_collection_exists_api"


# 初始化VectorDB Client
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root')


# 创建Database
# exists_db 使用示例
db_exists = vdb_client.exists_db(database_name=db_name)
print(f'Database {db_name} exists={db_exists}')

# create_database_if_not_exists 使用示例
db = vdb_client.create_database_if_not_exists(database_name=db_name)
print(f'Database {db_name} exists={vdb_client.exists_db(database_name=db_name)}')


# 创建Collection
# exists_collection 使用示例
coll_exists = vdb_client.exists_collection(database_name=db_name, collection_name=coll_name)
print(f'Collection {coll_name} exists={coll_exists}')
index = Index()
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
index.add(VectorIndex('vector', 32, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))

# create_collection_if_not_exists 使用示例
coll = db.create_collection_if_not_exists(
    name=coll_name,
    shard=1,
    replicas=0,
    description='test collection',
    index=index,
)
print(f'Collection {coll_name} exists={vdb_client.exists_collection(database_name=db_name, collection_name=coll_name)}')


# 清除环境
vdb_client.drop_database(db_name)
vdb_client.close()
