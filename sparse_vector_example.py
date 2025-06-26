import json
from typing import Optional, List
import tcvectordb
from tcvectordb.model.document import Document, AnnSearch, WeightedRerank, RRFRerank, KeywordSearch
from tcvectordb.model.enum import FieldType, IndexType, MetricType, ReadConsistency
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams, SparseVector, SparseIndex
from tcvdb_text.encoder import BM25Encoder
import numpy as np

# disable/enable http request log print
tcvectordb.debug.DebugEnable = False


vecs: List[List[float]] = np.random.rand(5, 768).tolist()


class Example:

    def __init__(self,
                 url: str,
                 key: str,
                 username: str = "root",
                 timeout: int = 30,
                 db_name: str ='python-sdk2-test-sparsevector',
                 coll_name: str = 'sdk2_collection-sparsevector'):
        """Create VectorDBClient"""
        self._client = tcvectordb.RPCVectorDBClient(url=url,
                                                    username=username,
                                                    key=key,
                                                    read_consistency=ReadConsistency.EVENTUAL_CONSISTENCY,
                                                    timeout=timeout)
        self.bm25 = BM25Encoder.default('zh')
        self.db_name = db_name
        self.coll_name = coll_name

    def create_database(self):
        print('========1.2 Create Database: {}'.format(self.db_name), flush=True)
        self._client.create_database_if_not_exists(database_name=self.db_name)

    @staticmethod
    def get_index():
        index = Index()
        index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
        index.add(VectorIndex('vector', 768, IndexType.HNSW, MetricType.IP,
                              HNSWParams(m=16, efconstruction=200)))
        index.add(SparseIndex(name='sparse_vector',
                              field_type=FieldType.SparseVector,
                              index_type=IndexType.SPARSE_INVERTED,
                              metric_type=MetricType.IP,
                              ))
        return index

    def create_collection(self, ):
        print('========2 Create Collection: {}'.format(self.coll_name), flush=True)
        coll = self._client.create_collection_if_not_exists(
            database_name=self.db_name,
            collection_name=self.coll_name,
            shard=1,
            replicas=0,
            description='test collection',
            index=Example.get_index(),
            timeout=10,
        )
        print(vars(coll), flush=True)

    def collection_info(self):
        print('========3 Describe Collection:', flush=True)
        coll = self._client.describe_collection(database_name=self.db_name,
                                                collection_name=self.coll_name)
        print(json.dumps(vars(coll), indent=2), flush=True)

    def upsert_data(self):
        sparse_vectors: List[SparseVector] = self.bm25.encode_texts([
            '腾讯云向量数据库（Tencent Cloud VectorDB）是一款全托管的自研企业级分布式数据库服务，专用于存储、索引、检索、管理由深度神经网络或其他机器学习模型生成的大量多维嵌入向量。',
            '作为专门为处理输入向量查询而设计的数据库，它支持多种索引类型和相似度计算方法，单索引支持10亿级向量规模，高达百万级 QPS 及毫秒级查询延迟。',
            '不仅能为大模型提供外部知识库，提高大模型回答的准确性，还可广泛应用于推荐系统、NLP 服务、计算机视觉、智能客服等 AI 领域。',
            '腾讯云向量数据库（Tencent Cloud VectorDB）作为一种专门存储和检索向量数据的服务提供给用户， 在高性能、高可用、大规模、低成本、简单易用、稳定可靠等方面体现出显著优势。 ',
            '腾讯云向量数据库可以和大语言模型 LLM 配合使用。企业的私域数据在经过文本分割、向量化后，可以存储在腾讯云向量数据库中，构建起企业专属的外部知识库，从而在后续的检索任务中，为大模型提供提示信息，辅助大模型生成更加准确的答案。',
        ])
        print('========4.1 Upsert docs:', flush=True)
        res = self._client.upsert(
            database_name=self.db_name,
            collection_name=self.coll_name,
            documents=[
                Document(id='0001',
                         vector=vecs[0],
                         sparse_vector=sparse_vectors[0],
                         ),
                Document(id='0002',
                         vector=vecs[1],
                         sparse_vector=sparse_vectors[1],
                         ),
                Document(id='0003',
                         vector=vecs[2],
                         sparse_vector=sparse_vectors[2],
                         ),
                Document(id='0004',
                         vector=vecs[3],
                         sparse_vector=sparse_vectors[3],
                         ),
                Document(id='0005',
                         vector=vecs[4],
                         sparse_vector=sparse_vectors[4],
                         )
            ]
        )
        print(res, flush=True)

    def search(self):
        print('========5.1 HybridSearch:', flush=True)
        res = self._client.hybrid_search(
            database_name=self.db_name,
            collection_name=self.coll_name,
            ann=[
                AnnSearch(
                    field_name="vector",
                    data=vecs[0],
                    limit=2,
                )
            ],
            match=[
                KeywordSearch(
                    field_name="sparse_vector",
                    data=self.bm25.encode_queries('腾讯云向量数据库'),
                    limit=3,
                ),
            ],
            rerank=WeightedRerank(
                field_list=['vector', 'sparse_vector'],
                weight=[0.6, 0.4],
            ),
            # rerank=RRFRerank(
            #     k=1,
            # ),
            retrieve_vector=False,
            limit=2,
        )
        for doc in res:
            print(json.dumps(doc, indent=2, ensure_ascii=False))

    def delete_db(self):
        print('========6 Delete Database:', flush=True)
        res = self._client.drop_database(self.db_name)
        print(res)

    def example(self):
        self.create_database()
        self.create_collection()
        try:
            self.collection_info()
            self.upsert_data()
            self.search()
        finally:
            self.delete_db()
            self._client.close()


if __name__ == '__main__':
    example = Example('vdb http url or ip and post', key='key get from web console', username='root')
    # example = Example('http://127.0.0.1:8100', key='vdb-key', username='root')
    example.example()
