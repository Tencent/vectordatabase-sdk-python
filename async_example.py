# async_example.py examples for async interface
import asyncio
import time

import tcvectordb
from tcvectordb.asyncapi.client.stub import AsyncVectorDBClient
from tcvectordb.asyncapi.model.collection import AsyncCollection
from tcvectordb.asyncapi.model.collection_view import AsyncCollectionView
from tcvectordb.asyncapi.model.database import AsyncDatabase
from tcvectordb.asyncapi.model.document_set import AsyncDocumentSet
from tcvectordb.model.collection_view import Embedding, SplitterProcess, Language
from tcvectordb.model.document import Filter, Document, HNSWSearchParams
from tcvectordb.model.document_set import Rerank
from tcvectordb.model.enum import FieldType, IndexType, MetricType
from tcvectordb.model.index import Index, FilterIndex, VectorIndex, HNSWParams

# disable/enable http request log print
tcvectordb.debug.DebugEnable = False


class AsyncExample:

    def __init__(self, url: str, key: str, username: str = 'root', timeout: int = 30):
        self.url = url
        self.key = key
        self.username = username
        self.timeout = timeout

    async def simple(self):
        db_name = 'async_test_simple_db'
        coll_name = 'async_test_simple_coll'
        coll_alias = 'async_test_simple_alias'
        # client
        client = AsyncVectorDBClient(url=self.url, key=self.key, username=self.username, timeout=self.timeout)
        try:
            # database
            db = await client.create_database(db_name)
            dbs = await client.list_databases()
            db: AsyncDatabase = await client.database(db_name)
            # collection
            index = Index()
            index.add(VectorIndex('vector', 3, IndexType.HNSW, MetricType.COSINE, HNSWParams(m=16, efconstruction=200)))
            index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
            index.add(FilterIndex('bookName', FieldType.String, IndexType.FILTER))
            index.add(FilterIndex('page', FieldType.Uint64, IndexType.FILTER))
            coll = await db.create_collection(
                name=coll_name,
                shard=1,
                replicas=0,
                description='test collection',
                index=index,
                embedding=None,
                timeout=20
            )
            res = await db.set_alias(coll_name, coll_alias)
            colls = await db.list_collections()
            coll = await db.describe_collection(coll_name)
            res = await db.delete_alias(coll_alias)
            coll: AsyncCollection = await db.collection(coll_name)
            # document
            document_list = [
                Document(id='0001',
                         vector=[0.2123, 0.21, 0.213],
                         bookName='西游记',
                         author='吴承恩',
                         page=21,
                         segment='富贵功名，前缘分定，为人切莫欺心。'),
                Document(id='0002',
                         vector=[0.2123, 0.22, 0.213],
                         bookName='西游记',
                         author='吴承恩',
                         page=22,
                         segment='正大光明，忠良善果弥深。些些狂妄天加谴，眼前不遇待时临。'),
                Document(id='0003',
                         vector=[0.2123, 0.23, 0.213],
                         bookName='三国演义',
                         author='罗贯中',
                         page=23,
                         segment='细作探知这个消息，飞报吕布。'),
                Document(id='0004',
                         vector=[0.2123, 0.24, 0.213],
                         bookName='三国演义',
                         author='罗贯中',
                         page=24,
                         segment='布大惊，与陈宫商议。宫曰：“闻刘玄德新领徐州，可往投之。”布从其言，竟投徐州来。有人报知玄德。'),
                Document(id='0005',
                         vector=[0.2123, 0.25, 0.213],
                         bookName='三国演义',
                         author='罗贯中',
                         page=25,
                         segment='玄德曰：“布乃当今英勇之士，可出迎之。”糜竺曰：“吕布乃虎狼之徒，不可收留；收则伤人矣。'),

            ]
            filter = Filter('bookName="三国演义"')
            res = await coll.upsert(documents=document_list)
            res = await coll.query(document_ids=["0001", "0002", "0003", "0004", "0005"],
                                   retrieve_vector=True, limit=2, offset=1,
                                   filter=filter, output_fields=["id", "bookName"])
            res = await coll.search(
                vectors=[[0.3123, 0.43, 0.213], [0.233, 0.12, 0.97]],
                params=HNSWSearchParams(ef=200),
                retrieve_vector=False,
                limit=10
            )
            res = await coll.searchById(
                document_ids=['0003'],
                params=HNSWSearchParams(ef=100),
                retrieve_vector=False,
                limit=2,
                filter=filter
            )
            res = await coll.update(data=Document(page=28), document_ids=["0001", "0003"], filter=Filter('bookName="三国演义"'))
            res = await coll.delete(document_ids=["0001", "0003"], filter=Filter('bookName="三国演义"'))
            # await coll.rebuild_index()
            # clear
            res = await db.truncate_collection(collection_name=coll_name)
            res = await db.drop_collection(coll_name)
        finally:
            res = await client.drop_database(db_name)
            client.close()

    async def ai(self):
        # init
        db_name = 'async_test_ai_db'
        coll_name = 'async_test_ai_coll'
        coll_alias = 'async_test_ai_alias'
        # client
        client = AsyncVectorDBClient(url=self.url, key=self.key, username=self.username, timeout=self.timeout)
        try:
            # database
            db = await client.create_ai_database(db_name)
            dbs = await client.list_databases()
            db = await client.database(db_name)
            # collection_view
            index = Index()
            index.add(FilterIndex('teststr', FieldType.String, IndexType.FILTER))
            index.add(FilterIndex('testList', FieldType.Array, IndexType.FILTER))
            cv = await db.create_collection_view(
                name=coll_name,
                description='desc',
                embedding=Embedding(
                    language=Language.ZH.value,
                    enable_words_embedding=True,
                ),
                splitter_process=SplitterProcess(
                    append_title_to_chunk=True,
                    append_keywords_to_chunk=True,
                ),
                index=index,
                timeout=100,
            )
            res = await db.set_alias(coll_name, coll_alias)
            cv = await db.describe_collection_view(coll_name)
            cvs = await db.list_collection_view()
            res = await db.delete_alias(coll_alias)
            cv: AsyncCollectionView = await db.collection_view(coll_name)
            # document_set
            ds = await cv.load_and_split_text(
                local_file_path='./tests/files/tcvdb.md',
                # document_set_name='tencent_vectordb.md',
                metadata={
                    'teststr': 'v1',
                    'filekey': 1024,
                    'author': 'sum',
                    'testList': ['a', 'b', 'c'],
                },
                splitter_process=SplitterProcess(
                    append_keywords_to_chunk=False,
                    append_title_to_chunk=False,
                ),
            )
            time.sleep(10)
            res = await cv.search(
                content='什么是向量数据库',
                expand_chunk=[1, 0],
                rerank=Rerank(
                    enable=False,
                    expect_recall_multiples=3,
                ),
                filter=Filter('teststr="v1"'),
                limit=2,
            )
            res = await cv.query(document_set_id=[ds.id])
            ds: AsyncDocumentSet = await cv.get_document_set(document_set_id=ds.id)
            res = await cv.update(
                data=Document(teststr='v2'),
                filter=Filter('teststr="v1"'),
                document_set_id=ds.id,
                document_set_name=ds.name
            )
            res = await ds.get_text()
            res = await ds.get_chunks()
            # clear
            res = await cv.delete(document_set_id=ds.id)
            res = await db.truncate_collection_view(coll_name)
            res = await db.drop_collection_view(coll_name)
        finally:
            res = await client.drop_ai_database(db_name)
            client.close()


if __name__ == '__main__':
    example = AsyncExample(url='vdb http url or ip and post', key='key get from web console')
    asyncio.run(example.simple())
    asyncio.run(example.ai())
