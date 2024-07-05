from typing import Optional, List

from cachetools import cached, TTLCache
from requests.adapters import HTTPAdapter

from tcvectordb import VectorDBClient
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.database import Database
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.rpc.client.rpcclient import RPCClient
from tcvectordb.rpc.model.database import RPCDatabase, db_convert


class RPCVectorDBClient(VectorDBClient):
    """
    RPCVectorDBClient create a grpc client for database operate.
    """

    def __init__(self,
                 url: str,
                 username='',
                 key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10,
                 channel_ready_check: bool = True,
                 ):
        super().__init__(url, username, key, read_consistency, timeout, adapter, pool_size=pool_size)
        self.rpc_client = RPCClient(url=url,
                                    username=username,
                                    key=key,
                                    timeout=timeout,
                                    channel_ready_check=channel_ready_check)

    def create_database(self, database_name: str, timeout: Optional[float] = None) -> RPCDatabase:
        sdb = super().create_database(database_name=database_name, timeout=timeout)
        return db_convert(sdb, self.rpc_client)

    def list_databases(self, timeout: Optional[float] = None) -> List[Database]:
        sdbs = super().list_databases(timeout=timeout)
        dbs = []
        for sdb in sdbs:
            if isinstance(sdb, AIDatabase):
                dbs.append(sdb)
            else:
                dbs.append(db_convert(sdb, self.rpc_client))
        return sdbs

    @cached(cache=TTLCache(maxsize=1024, ttl=3))
    def database(self, database: str) -> RPCDatabase:
        sdb = super().database(database)
        return db_convert(sdb, self.rpc_client)

    def close(self):
        super().close()
        self.rpc_client.close()
