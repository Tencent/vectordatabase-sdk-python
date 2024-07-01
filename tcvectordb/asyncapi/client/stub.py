from typing import List, Optional, Union

from requests.adapters import HTTPAdapter

from tcvectordb import VectorDBClient, exceptions
from tcvectordb.asyncapi.model.ai_database import AsyncAIDatabase
from tcvectordb.asyncapi.model.database import AsyncDatabase
from tcvectordb.model.enum import ReadConsistency


class AsyncVectorDBClient(VectorDBClient):

    def __init__(self,
                 url=None,
                 username='',
                 key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10):
        super().__init__(url, username, key, read_consistency, timeout, adapter, pool_size=pool_size)

    async def create_database(self, database_name: str, timeout: Optional[float] = None) -> AsyncDatabase:
        db = AsyncDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        await db.create_database(timeout=timeout)
        return db

    async def create_ai_database(self, database_name: str, timeout: Optional[float] = None) -> AsyncAIDatabase:
        db = AsyncAIDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        await db.create_database(timeout=timeout)
        return db

    async def drop_database(self, database_name: str, timeout: Optional[float] = None):
        return super().drop_database(database_name, timeout)

    async def drop_ai_database(self, database_name: str, timeout: Optional[float] = None):
        return super().drop_ai_database(database_name, timeout)

    async def list_databases(self, timeout: Optional[float] = None) -> List[Union[AsyncDatabase, AsyncAIDatabase]]:
        db = AsyncDatabase(conn=self._conn, read_consistency=self._read_consistency)
        dbs = await db.list_databases(timeout=timeout)
        return dbs

    async def database(self, database: str) -> Union[AsyncDatabase, AsyncAIDatabase]:
        dbs = await self.list_databases()
        for db in dbs:
            if db.database_name == database:
                return db
        raise exceptions.ParamError(message='Database not exist: {}'.format(database))

