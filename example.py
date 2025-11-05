# example.py demonstrates the basic operations of tcvectordb, a Python SDK of tencent cloud vectordb.
import json

import numpy as np
from examples.data import NosqlProduct
import tcvectordb
from tcvectordb.model.enum import FieldType, IndexType, MetricType, ReadConsistency
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams

# disable/enable http request log print
tcvectordb.debug.DebugEnable = False


class TestVDB:

    def __init__(self, url: str, key: str, username: str = 'root', timeout: int = 30, drop: bool = False):
        """Init client, create database and collection."""
        self.database_name = "python-sdk-test-database"
        self.collection_name = "nosql_product"
        self.client = tcvectordb.RPCVectorDBClient(url=url,
                                                   key=key,
                                                   username=username,
                                                   read_consistency=ReadConsistency.EVENTUAL_CONSISTENCY,
                                                   timeout=timeout)
        if drop:
            self.client.drop_database(database_name=self.database_name)
        self.client.create_database_if_not_exists(database_name=self.database_name)
        self._create_collection_if_not_exists()
        self.vecs: list = np.random.rand(6, 64).tolist()

    def _create_collection_if_not_exists(self):
        # Create Collection
        self.client.create_collection_if_not_exists(
            database_name=self.database_name,
            collection_name=self.collection_name,
            shard=1,
            replicas=1,
            indexes=[
                FilterIndex(name='id', field_type=FieldType.String, index_type=IndexType.PRIMARY_KEY),
                VectorIndex(name='vector', field_type=FieldType.Vector, index_type=IndexType.HNSW,
                            dimension=64, metric_type=MetricType.COSINE, params=HNSWParams(m=16, efconstruction=200)),
                FilterIndex(name='name', field_type=FieldType.String, index_type=IndexType.FILTER),
                FilterIndex(name='type', field_type=FieldType.String, index_type=IndexType.FILTER),
                FilterIndex(name='release', field_type=FieldType.Uint64, index_type=IndexType.FILTER),
            ]
        )

    def upsert_data(self):
        # Upsert test data
        documents = [{
            "id": f'000{i+1}',
            "vector": self.vecs[i],
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

    def query_example(self):
        # query example
        res = self.client.query(
            database_name=self.database_name,
            collection_name=self.collection_name,
            document_ids=["0001", "0002", "0003", "0004"],
            filter="release=2020",
            output_fields=["name", "type", "release"],
            limit=10,
        )
        print("query result:", res)

    def search_example(self):
        # search by vector
        res = self.client.search(
            database_name=self.database_name,
            collection_name=self.collection_name,
            vectors=[self.vecs[5]],
            output_fields=["name", "type", "release"],
            limit=2,
        )
        print("search_by_vector result:", res)
        # search by id
        res = self.client.search_by_id(
            database_name=self.database_name,
            collection_name=self.collection_name,
            document_ids=["0001"],
            output_fields=["name", "type", "release"],
            limit=2,
        )
        print("search_by_id result:", res)

    def update_example(self):
        # update example
        res = self.client.update(
            database_name=self.database_name,
            collection_name=self.collection_name,
            data={
                "description": "腾讯云向量数据库（Tencent Cloud VectorDB）是一款全托管的自研企业级分布式数据库服务，"
                               "专用于存储、索引、检索、管理由深度神经网络或其他机器学习模型生成的大量多维嵌入向量。"
            },
            document_ids=["0006"],
            filter="type=\"向量\"",
        )
        print("update result:", res)

    def delete_and_truncate_example(self):
        # delete doc example
        res = self.client.delete(
            database_name=self.database_name,
            collection_name=self.collection_name,
            document_ids=["0001", "0002"],
            filter="release=2020",
        )
        print("delete result:", res)
        # truncate collection example
        res = self.client.truncate_collection(
            database_name=self.database_name,
            collection_name=self.collection_name,
        )
        print("truncate_collection result:", res)

    def drop_example(self):
        # drop collection example
        res = self.client.drop_collection(
            database_name=self.database_name,
            collection_name=self.collection_name,
        )
        print("drop_collection result:", res)
        # drop database example
        res = self.client.drop_database(
            database_name=self.database_name
        )
        print("drop_database result:", res)

    def close(self):
        self.client.close()


if __name__ == '__main__':
    test_vdb = TestVDB('vdb http url or ip and post', key='key get from web console')
    # test_vdb = TestVDB('http://127.0.0.1:8100', key='vdb-key', username='root')
    test_vdb.upsert_data()
    test_vdb.query_example()
    test_vdb.search_example()
    test_vdb.update_example()
    test_vdb.delete_and_truncate_example()
    test_vdb.drop_example()
    test_vdb.close()
