from typing import Optional, List, Dict, Any

from tcvectordb.asyncapi.model.collection_view import AsyncCollectionView
from tcvectordb.client.httpclient import HTTPClient
from tcvectordb.model.ai_database import AIDatabase
from tcvectordb.model.collection_view import SplitterProcess, Embedding, CollectionView
from tcvectordb.model.enum import ReadConsistency
from tcvectordb.model.index import Index


class AsyncAIDatabase(AIDatabase):

    def __init__(self,
                 conn: HTTPClient,
                 name: str,
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY):
        super().__init__(conn, name, read_consistency)

    async def create_database(self, database_name='', timeout: Optional[float] = None):
        super().create_database(database_name, timeout)

    async def drop_database(self, database_name='', timeout: Optional[float] = None) -> Dict[str, Any]:
        return super().drop_database(database_name, timeout)

    async def create_collection_view(
            self,
            name: str,
            description: str = '',
            embedding: Optional[Embedding] = None,
            splitter_process: Optional[SplitterProcess] = None,
            index: Optional[Index] = None,
            timeout: Optional[float] = None,
    ) -> AsyncCollectionView:
        cv = super().create_collection_view(name,
                                            description,
                                            embedding,
                                            splitter_process,
                                            index,
                                            timeout)
        return cv_convert(cv)

    async def describe_collection_view(self,
                                       collection_view_name: str,
                                       timeout: Optional[float] = None) -> AsyncCollectionView:
        cv = super().describe_collection_view(collection_view_name, timeout)
        return cv_convert(cv)

    async def list_collection_view(self, timeout: Optional[float] = None) -> List[AsyncCollectionView]:
        cvs = super().list_collection_view(timeout)
        return [cv_convert(cv) for cv in cvs]

    async def collection_view(self,
                              collection_view_name: str,
                              timeout: Optional[float] = None) -> AsyncCollectionView:
        return await self.describe_collection_view(collection_view_name, timeout)

    async def drop_collection_view(self,
                                   collection_view_name: str,
                                   timeout: Optional[float] = None
                                   ) -> Dict[str, Any]:
        return super().drop_collection_view(collection_view_name, timeout)

    async def truncate_collection_view(self,
                                       collection_view_name: str,
                                       timeout: Optional[float] = None) -> Dict[str, Any]:
        return super().truncate_collection_view(collection_view_name, timeout)

    async def set_alias(self,
                        collection_view_name: str,
                        alias: str,
                        ) -> Dict[str, Any]:
        return super().set_alias(collection_view_name, alias)

    async def delete_alias(self, alias: str) -> Dict[str, Any]:
        return super().delete_alias(alias)


def cv_convert(coll: CollectionView) -> AsyncCollectionView:
    return AsyncCollectionView(
        db=coll.db,
        name=coll.name,
        description=coll.description,
        embedding=coll.embedding,
        splitter_process=coll.splitter_process,
        index=coll.index
    )
