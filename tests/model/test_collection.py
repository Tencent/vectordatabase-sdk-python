import unittest
from unittest import mock

import requests
from tcvectordb.model.enum import EmbeddingModel

from tcvectordb.model.document import Filter

from tcvectordb.client.httpclient import HTTPClient, Response
from tcvectordb.model.collection import Collection, Embedding
from tcvectordb.model.database import Database


class TestEmbedding(unittest.TestCase):

    def test_init(self):
        embedding1 = Embedding(vector_field="vector", field="text", model=EmbeddingModel.BGE_BASE_ZH)
        self.assertEqual(vars(embedding1),
                         {'status': 'disabled', 'field': 'text', 'model': 'bge-base-zh', 'vectorField': 'vector'})
        embedding2 = Embedding(vector_field="vector", field="text", model_name="bge_large_zh")
        self.assertEqual(vars(embedding2),
                         {'status': 'disabled', 'field': 'text', 'model': 'bge_large_zh', 'vectorField': 'vector'})
        embedding3 = Embedding(vector_field="vector", field="text", model=EmbeddingModel.BGE_BASE_ZH,
                               model_name="bge_large_zh")
        self.assertEqual(vars(embedding3),
                         {'status': 'disabled', 'field': 'text', 'model': 'bge_large_zh', 'vectorField': 'vector'})


class TestCollection(unittest.TestCase):
    """test **kwargs"""

    def test_upsert_01(self):
        requests.Session = mock.Mock(return_value=None)
        mock_obj = HTTPClient(url="localhost:8100", username="root", key="key")
        mock_obj.post = mock.Mock(return_value="1")

        # test
        db = Database(conn=mock_obj)
        coll = Collection(db=db)
        coll.upsert(documents=[], build_index=False, buildIndex=False)
        coll.upsert(documents=[], build_index=False, buildIndex=True)
        coll.upsert(documents=[], build_index=True, buildIndex=False)
        coll.upsert(buildIndex=False, documents=[], build_index=True)

    def test_query_01(self):
        mock_requests_response = requests.Response()
        mock_requests_response.json = mock.Mock(return_value={"code": 0})
        mock_response = Response(path="", res=mock_requests_response)

        requests.Session = mock.Mock(return_value=None)
        mock_http_client = HTTPClient(url="localhost:8100", username="root", key="key")
        mock_http_client.post = mock.Mock(return_value=mock_response)

        # test
        db = Database(conn=mock_http_client)
        coll = Collection(db=db)
        coll.query(document_ids=[])
        coll.query()

    def test_delete_01(self):
        requests.Session = mock.Mock(return_value=None)
        mock_obj = HTTPClient(url="localhost:8100", username="root", key="key")
        mock_obj.post = mock.Mock(return_value="1")

        # test
        db = Database(conn=mock_obj, name="test_database")
        coll = Collection(db=db, name="test_coll")
        coll.delete()
        coll.delete(document_ids=[])
        coll.delete(filter=Filter(cond=""))


# 运行测试
if __name__ == '__main__':
    unittest.main()
