# ai_db_example.py  AI套件相关接口使用示例

import json
import time
from typing import Optional

import tcvectordb
from tcvectordb import exceptions
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.collection_view import Embedding, SplitterProcess, Language, CollectionView
from tcvectordb.model.document import Filter, Document
from tcvectordb.model.document_set import DocumentSet, Rerank
from tcvectordb.model.enum import FieldType, IndexType, ReadConsistency
from tcvectordb.model.index import Index, FilterIndex

# disable/enable http request log print
tcvectordb.debug.DebugEnable = False


class AiDocExample:

    def __init__(self, url: str, key: str, username: str = 'root'):
        """
        初始化客户端
        """
        # 创建客户端时可以指定 read_consistency，后续调用 sdk 接口的 read_consistency 将延用该值
        self._client = tcvectordb.VectorDBClient(url=url,
                                                 key=key,
                                                 username=username,
                                                 timeout=50,
                                                 read_consistency=ReadConsistency.STRONG_CONSISTENCY)
        self.ai_db: Optional[AIDatabase] = None
        self.coll_view: Optional[CollectionView] = None
        self.doc_set_id: Optional[int] = None
        self.doc_set_name: Optional[str] = None

    def link_ai_database(self, db_name='python-sdk-test-ai-doc'):
        # 连接已存在的AIDatabase
        self.ai_db = self._client.database(db_name)
        return

    def create_ai_database(self, db_name='python-sdk-test-ai-doc'):
        # 检查并清理同名Database
        print('========1.1 检查并清理同名Database')
        try:
            db = self._client.database(db_name)
            if db:
                self._client.drop_ai_database(db_name)
        except exceptions.ParamError:
            pass
        print('========1.2 创建AI Database: {}'.format(db_name))
        # 创建 AI 类向量数据库
        db = self._client.create_ai_database(db_name)
        self.ai_db = db
        print("========1.3 列举所有Database: ")
        # 用于查询集群中存在的所有数据库
        database_list = self._client.list_databases()
        for db in database_list:
            print("name={}, type={}".format(db.database_name, db.__class__.__name__))

    def link_collection_view(self, coll_name='ai_doc_collection'):
        # 连接已存在的CollectionView
        self.coll_view = self.ai_db.collection_view(coll_name)
        return

    def create_collection_view(self, coll_name='ai_doc_collection'):
        print('========2 创建CollectionView: {}'.format(coll_name))
        # 在已创建的AI类Database中创建 CollectionView
        index = Index()
        index.add(FilterIndex('teststr', FieldType.String, IndexType.FILTER))
        index.add(FilterIndex('testList', FieldType.Array, IndexType.FILTER))
        self.coll_view = self.ai_db.create_collection_view(
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
        print(vars(self.coll_view))

    def collection_view_info(self):
        print('========3.1 List CollectionView:')
        # 查询指定AI类Database 中所有的 CollectionView。
        coll_list = self.ai_db.list_collection_view()
        self.print_object(coll_list)
        print('========3.2 Describe CollectionView:')
        # 用于查询指定CollectionView 的信息
        coll = self.ai_db.describe_collection_view(self.coll_view.name)
        print(json.dumps(vars(coll), indent=2))

    def upload_file(self, file_path):
        print('========4 上传文件: {}'.format(file_path))
        # 上传本地文件，并解析到AI database
        #    可用document_set_name做为导入文件名
        #    支持自定义属性：metadata
        doc_set = self.coll_view.load_and_split_text(
            local_file_path=file_path,
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
        print(vars(doc_set))
        self.doc_set_id = doc_set.id
        self.doc_set_name = doc_set.name

    def document_set_info(self):
        res = self.coll_view.query(limit=1)
        self.doc_set_id = res[0].id
        self.doc_set_name = res[0].name
        print('========5.1 Get DocumentSet:')
        # 查询指定CollectionView中所有的DocumentSet
        ds = self.coll_view.get_document_set(document_set_id=self.doc_set_id)
        print(json.dumps(vars(ds), indent=2, ensure_ascii=False))
        print('========5.2 Get DocumentSet Text:')
        # 查询指定CollectionView中所有的DocumentSet
        if ds.get_text():
            print(ds.get_text()[:100])
        print('========5.3 Get DocumentSet Chunks:')
        res = ds.get_chunks(limit=3, offset=0)
        print(res[0].start_pos)
        print(res[0].end_pos)
        print(res[0].text)
        self.print_object(res)

    def query_and_search(self):
        print('========6.1 Query:')
        # 用于精确查找与查询条件完全匹配的文件，具体支持如下功能。
        #     支持对文件名使用 Filter 索引的方式查询文件信息。
        #     支持指定查询起始位置 offset 和返回数量 limit，实现数据 SCAN 能力。
        #     支持根据主键 id（Document ID），搭配自定义的标量字段的 Filter 表达式一并检索。
        res = self.coll_view.query(document_set_id=[self.doc_set_id])
        self.print_object(res)
        print('========6.2 Search:')
        # 查找与给定查询向量相似的向量。支持输入文本信息检索与输入文本相似的内容，同时，支持搭配标量字段的 Filter 表达式一并检索。
        res = self.coll_view.search(
            content='什么是向量数据库',
            expand_chunk=[1, 0],
            rerank=Rerank(
                enable=True,
                expect_recall_multiples=3,
            ),
            filter=Filter('teststr="v1"'),
            limit=2,
        )
        self.print_object(res)

    def update_and_delete(self):
        print('========7.1 Update:')
        # 通过document_set_id、document_set_name、Filter表达式过滤检索 DocumentSet ，
        # 对 DocumentSet 的部分字段进行更新。同时，支持新增字段。
        filter_param = Filter('teststr="v1"')
        update = Document(teststr='v2')
        print(self.coll_view.update(data=update, filter=filter_param,
                                    document_set_id=self.doc_set_id,
                                    document_set_name=self.doc_set_name))
        time.sleep(2)
        print('========7.2 Query By ID:')
        res = self.coll_view.query(document_set_id=[self.doc_set_id])
        self.print_object(res)
        print('========7.3 Delete:')
        # 接口用于删除指定document_set_id、document_set_name的文件，且支持设置 Filter 表达式，删除满足 Filter 表达式的文件
        print(self.coll_view.delete(document_set_id=self.doc_set_id, document_set_name=self.doc_set_name))
        time.sleep(2)
        print('========7.4 Query By Name:')
        res = self.coll_view.query(document_set_name=[self.doc_set_name])
        self.print_object(res)

    def alias_api_example(self):
        print('========8.1 Set Alias:')
        # 为 AI 类 CollectionSet 指定别名。别名可以是一个简短的字符串，
        # 方便标识和访问对应的集合。通常，别名会替换 CollectionSet 名称用于业务切换 Embedding 模型等场景。
        # 一个 CollectionSet 可以设置一个或者多个别名。
        print(self.ai_db.set_alias(self.coll_view.name, 'my_alias'))
        time.sleep(5)
        print('========8.2 Delete Alias:')
        # 删除 Ai 类数据库指定的集合的别名
        print(self.ai_db.delete_alias('my_alias'))

    def clear_collection_view_data(self):
        print('========9.1 Truncate CollectionView:')
        # 清空CollectionSet，包含 CollectionSet 中的所有文档
        print(self.ai_db.truncate_collection_view(self.coll_view.name, timeout=100))
        print('========9.2 Delete CollectionView:')
        # 删除指定CollectionSet，包含 CollectionSet 中的所有文档
        print(self.ai_db.drop_collection_view(self.coll_view.name))

    def delete_db(self):
        # 删除已创建的AIDatabase，并删除 AIDatabase 中所有 CollectionView 以及 DocumentSet
        print('========10 Delete AI Database:')
        print(self._client.drop_ai_database(self.ai_db.database_name))
        self._client.close()

    def print_object(self, obj):
        for elem in obj:
            if hasattr(elem, '__dict__'):
                print(json.dumps(vars(elem), indent=2, ensure_ascii=False))
            else:
                print(json.dumps(elem, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    example = AiDocExample(url='vdb http url or ip and post',
                           key='key get from web console',
                           username='vdb username')
    example.create_ai_database()
    example.create_collection_view()
    # example.link_ai_database()
    # example.link_collection_view()
    try:
        time.sleep(3)
        example.collection_view_info()
        example.upload_file("./tests/files/tcvdb.md")
        time.sleep(15)  # wait file parse
        example.document_set_info()
        example.query_and_search()
        example.update_and_delete()
        example.alias_api_example()
        example.clear_collection_view_data()
    finally:
        # pass
        example.delete_db()
