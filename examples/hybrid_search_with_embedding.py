# use embedding in hybrid_search
import json
import time
from typing import List

import numpy as np

import tcvectordb
from tcvdb_text.encoder.bm25 import BM25Encoder
from tcvectordb.model.collection import Embedding
from tcvectordb.model.document import AnnSearch, KeywordSearch, WeightedRerank, HNSWSearchParams, RRFRerank
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams, SparseIndex, SparseVector

vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-emb"
coll_name = "sdk_collection_emb"

tcvectordb.debug.DebugEnable = False
# create VectorDBClient

vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root')
# vdb_client.drop_database(db_name)
# create Database
db = vdb_client.create_database_if_not_exists(database_name=db_name)
# create Collection with embedding
ebd = Embedding(vector_field='vector', field='text', model_name='bge-base-zh')
index = Index()
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
index.add(VectorIndex('vector', 768, IndexType.HNSW, MetricType.IP, HNSWParams(m=16, efconstruction=200)))
index.add(SparseIndex("sparse_vector", FieldType.SparseVector, IndexType.SPARSE_INVERTED, MetricType.IP))
coll = db.create_collection_if_not_exists(
    name=coll_name,
    shard=1,
    replicas=1,
    description='test collection',
    index=index,
    embedding=ebd,
)

texts = [
    '腾讯云向量数据库（Tencent Cloud VectorDB）是一款全托管的自研企业级分布式数据库服务，专用于存储、索引、检索、管理由深度神经网络或其他机器学习模型生成的大量多维嵌入向量。',
    '作为专门为处理输入向量查询而设计的数据库，它支持多种索引类型和相似度计算方法，单索引支持10亿级向量规模，高达百万级 QPS 及毫秒级查询延迟。',
    '不仅能为大模型提供外部知识库，提高大模型回答的准确性，还可广泛应用于推荐系统、NLP 服务、计算机视觉、智能客服等 AI 领域。',
    '腾讯云向量数据库（Tencent Cloud VectorDB）作为一种专门存储和检索向量数据的服务提供给用户， 在高性能、高可用、大规模、低成本、简单易用、稳定可靠等方面体现出显著优势。 ',
    '腾讯云向量数据库可以和大语言模型 LLM 配合使用。企业的私域数据在经过文本分割、向量化后，可以存储在腾讯云向量数据库中，构建起企业专属的外部知识库，从而在后续的检索任务中，为大模型提供提示信息，辅助大模型生成更加准确的答案。',
]

bm25 = BM25Encoder.default('zh')
sparse_vectors: List[SparseVector] = bm25.encode_texts(texts)
# upsert test data
res = vdb_client.upsert(
    database_name=db_name,
    collection_name=coll_name,
    documents=[
        {'id': '0001', 'text': texts[0], 'sparse_vector': sparse_vectors[0]},
        {'id': '0002', 'text': texts[1], 'sparse_vector': sparse_vectors[1]},
        {'id': '0003', 'text': texts[2], 'sparse_vector': sparse_vectors[2]},
        {'id': '0004', 'text': texts[3], 'sparse_vector': sparse_vectors[3]},
    ]
)
print(res, flush=True)
time.sleep(2)

print(vars(db.collection(coll_name)))

# search with text
res = vdb_client.hybrid_search(
    database_name=db_name,
    collection_name=coll_name,
    ann=[
        AnnSearch(
            field_name="text",
            data='什么是腾讯云数据库',
            limit=2,
        ),
    ],
    match=[
        KeywordSearch(
            field_name="sparse_vector",
            data=bm25.encode_queries('什么是腾讯云数据库'),
            limit=2,
            terminate_after=4000,
            cutoff_frequency=0.1,
        ),
    ],
    rerank=WeightedRerank(
        field_list=['vector', 'sparse_vector'],
        weight=[0.5, 0.5],
    ),
    retrieve_vector=False,
    limit=2,
)
print(json.dumps(res, indent=2, ensure_ascii=False))


# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
