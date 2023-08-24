# example.py demonstrates the basic operations of tcvectordb, a Python SDK of tencent cloud vectordb.
# 1. connect to vectordb and create database and collection
# 2. upsert data
# 3. query and search data
# 4. drop collection and database
import time
import json
import tcvectordb
from tcvectordb.exceptions import VectorDBException
from tcvectordb.model.enum import FieldType, IndexType, IndexType, MetricType
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams
from tcvectordb.model.document import Document, Filter, HNSWSearchParams


# disable/enable http request log print
tcvectordb.debug.DebugEnable = False

# create a database client object
client = tcvectordb.VectorDBClient(
    url='http://127.0.0.1', username='root', key='key get from web console', timeout=30)


def print_object(obj):
    for elem in obj:
        if hasattr(elem, '__dict__'):
            print(json.dumps(vars(elem), indent=2))
        else:
            print(json.dumps(elem, indent=2))


def init_db_collction():
    try:
        # drop a database
        print("drop database dbtest ...")
        client.drop_database('dbtest')

        # create a database
        print("create database dbtest ...")
        db = client.create_database('dbtest')

        # list databases
        print("list databases ...")
        print(db.list_databases())

        # create a collection

        # -- index config
        index = Index(
            FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY),
            FilterIndex('author', FieldType.String, IndexType.FILTER),
            FilterIndex('page', FieldType.Uint64, IndexType.FILTER),
            VectorIndex('vector', 3, IndexType.HNSW,
                        MetricType.L2, HNSWParams(64, 8))
        )

        # db.drop_collection('book')
        print("create collection book ...")
        res = coll = db.create_collection(
            name='book',
            shard=1,
            replicas=2,
            description='this is a collection of book context',
            index=index
        )

        # list collections
        print_object(db.list_collections())

        return 0

    except VectorDBException as e:
        print(e.message)
        return 1
    except Exception as ex:
        print(type(ex))
        print(ex)
        return 1


def upsert_data():
    try:
        # get collection object
        db = client.database('dbtest')
        coll = db.collection('book')

        print("upsert data ...")
        res = coll.upsert(
            documents=[
                Document(id='0001', vector=[
                         0.2123, 0.23, 0.213], author='jerry', page=21, section='1.1.1'),
                Document(id='0002', vector=[
                         0.2123, 0.22, 0.213], author='sam', page=22, section='1.1.2'),
                Document(id='0003', vector=[
                         0.2123, 0.21, 0.213], author='max', page=23, section='1.1.3')
            ]
        )
        time.sleep(1)
        return 0

    except VectorDBException as e:
        print(e.message)
        return 1
    except Exception as ex:
        print(type(ex))
        print(ex)
        return 1


def clear_db_coll():
    try:
        db = client.database('dbtest')
        coll = db.collection('book')

        # drop a collection
        print("drop collection book ...")
        db.drop_collection('book')

        print("list collections ...")
        print_object(db.list_collections())

        # drop a database
        print("drop database dbtest ...")
        db.drop_database('dbtest')

        print("list databases ...")
        print(db.list_databases())

        return 0

    except VectorDBException as e:
        print(e.message)
        return 1
    except Exception as ex:
        print(type(ex))
        print(ex)
        return 1


def query_data():
    try:
        db = client.database('dbtest')
        coll = db.collection('book')

        # query database with primary key
        print("query database with primary key ...")
        res = coll.query(['0001'])
        print_object(res)

        # search topn similary documents
        print("search topn similary documents ...")
        res = coll.search(
            vectors=[[0.3123, 0.43, 0.213]],
            params=HNSWSearchParams(10),
            limit=10
        )
        print_object(res)

        # search topn similary documents by documentId(PK),
        # Get the vector by id first, then use vector for search similary data
        print("search topn similary documents by documentId(PK) ...")
        res = coll.searchById(
            document_ids=['0001'],
            params=HNSWSearchParams(10),
            limit=10
        )
        print_object(res)

        # search topn similary documents with filter
        print("search topn similary documents with filter ...")
        res = coll.search(
            [[0.3123, 0.43, 0.213]],
            Filter('author="jerry"').And('page>20'),
            HNSWSearchParams(10),
            True,
            10,
        )
        print_object(res)

        # delete a document
        print("delete a document ...")
        coll.delete(['0003'])

        return 0

    except VectorDBException as e:
        print(e.message)
        return 1
    except Exception as ex:
        print(type(ex))
        print(ex)
        return 1


init_db_collction()
upsert_data()
query_data()
clear_db_coll()
