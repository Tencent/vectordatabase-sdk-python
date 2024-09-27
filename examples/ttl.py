# TTL使用示例
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


# 初始化VectorDB Client
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root')


# 创建Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)


# 创建Collection
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
    ttl_config={                                        # 配置TTL
        'enable': True,                                 # 开启TTL
        'timeField': 'expire_at'                        # 配置时间字段：doc将在expire_at设置的时间戳到达后失效
    }
)
print(coll.ttl_config)


# 插入数据
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
            'expire_at': int(time.time()) + 10*60,      # 本条doc将在10分钟后失效，并在下个检测周期被清除，检测周期为1小时
        }
    ]
)
print(res, flush=True)


# 查询数据
time.sleep(61*60)
res = coll.query(document_ids=['0001', '0002'])
print(res, flush=True)                                  # doc(0002)失效并被清除后将查询不到


# 清除环境
vdb_client.drop_database(db_name)
vdb_client.close()
