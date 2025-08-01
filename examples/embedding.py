# embedding example
import tcvectordb

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"

# tcvectordb.debug.DebugEnable = False

# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root',
                                          )
# embedding
print(vdb_client.embedding(model='bge-m3',
                           data=['什么是腾讯云向量数据库'],
                           params={
                               'retrieveDenseVector': True,
                               'retrieveSparseVector': False
                           },
                           data_type='text'))
vdb_client.close()
