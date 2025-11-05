# use embedding example
from examples.data import NosqlProduct
import tcvectordb
from tcvectordb.model.collection import Embedding
from tcvectordb.model.enum import FieldType, IndexType, MetricType, EmbeddingModel, ReadConsistency
from tcvectordb.model.index import VectorIndex, FilterIndex, HNSWParams

from example import TestVDB

# disable/enable http request log print
tcvectordb.debug.DebugEnable = False


class TestEmbedding(TestVDB):

    def __init__(self, url: str, key: str, username: str = 'root', timeout: int = 30, drop: bool = False):
        """Init client, create database and collection."""
        self.database_name = "python-sdk-test-database"
        self.collection_name = "nosql_product_emb"
        self.client = tcvectordb.RPCVectorDBClient(url=url,
                                                   key=key,
                                                   username=username,
                                                   read_consistency=ReadConsistency.EVENTUAL_CONSISTENCY,
                                                   timeout=timeout)
        if drop:
            self.client.drop_database(database_name=self.database_name)
        self.client.create_database_if_not_exists(database_name=self.database_name)
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        # Create Collection
        ebd = Embedding(vector_field='vector', field='description', model=EmbeddingModel.BGE_BASE_ZH)
        self.client.create_collection_if_not_exists(
            database_name=self.database_name,
            collection_name=self.collection_name,
            shard=1,
            replicas=0,
            indexes=[
                FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY),
                VectorIndex(name='vector', field_type=FieldType.Vector, index_type=IndexType.HNSW,
                            dimension=768, metric_type=MetricType.COSINE, params=HNSWParams(m=16, efconstruction=200)),
                FilterIndex(name='name', field_type=FieldType.String, index_type=IndexType.FILTER),
                FilterIndex(name='type', field_type=FieldType.String, index_type=IndexType.FILTER),
                FilterIndex(name='release', field_type=FieldType.Uint64, index_type=IndexType.FILTER),
            ],
            embedding=ebd,
        )

    def upsert_data(self):
        # Upsert test data
        documents = [{
            "id": f'000{i+1}',
            "name": NosqlProduct[i].get('name'),
            "release": NosqlProduct[i].get('release'),
            "description": NosqlProduct[i].get('description'),
            "features": NosqlProduct[i].get('features'),
            "type": NosqlProduct[i].get('type'),
        } for i in range(6)]
        res = self.client.upsert(
            database_name=self.database_name,
            collection_name=self.collection_name,
            documents=documents,
        )
        print("upsert result:", res)

    def search_example(self):
        # search by vector
        res = self.client.search_by_text(
            database_name=self.database_name,
            collection_name=self.collection_name,
            embedding_items=["向量数据库"],
            output_fields=["name", "type", "release"],
            limit=2,
            # retrieve_vector=True,
        )
        print("search_by_text result:", res)

    def update_example(self):
        # update example
        product = NosqlProduct[0]
        res = self.client.update(
            database_name=self.database_name,
            collection_name=self.collection_name,
            data={
                "description": "腾讯云向量数据库（Tencent Cloud VectorDB）是一款全托管的自研企业级分布式数据库服务，"
                               "专用于存储、索引、检索、管理由深度神经网络或其他机器学习模型生成的大量多维嵌入向量。"
            },
            document_ids=["0006"]
        )
        print("update result:", res)
        res = self.client.query(
            database_name=self.database_name,
            collection_name=self.collection_name,
            document_ids=["0006"],
            output_fields=["name", "type", "release", "description"],
            # retrieve_vector=True,
        )
        print("query result:", res)

    def drop_example(self):
        # drop database example
        res = self.client.drop_database(
            database_name=self.database_name
        )
        print("drop_database result:", res)

    def close(self):
        self.client.close()


if __name__ == '__main__':
    # test_vdb = TestEmbedding('vdb http url or ip and post', key='key get from web console')
    test_vdb = TestEmbedding('http://127.0.0.1:8100', key='vdb-key')
    test_vdb.upsert_data()
    test_vdb.search_example()
    test_vdb.update_example()
    test_vdb.drop_example()
    test_vdb.close()
