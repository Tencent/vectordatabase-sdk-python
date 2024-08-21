from typing import List, Optional, Union, Dict, Any
from requests.adapters import HTTPAdapter

from tcvectordb.model.enum import ReadConsistency

from .httpclient import HTTPClient
from tcvectordb.model.database import Database
from tcvectordb import exceptions
from tcvectordb.model.ai_database import AIDatabase
from ..model.collection import Collection
from ..model.document import Document, Filter


class VectorDBClient:
    """
    VectorDBClient create a http client session for database operate.
    """

    def __init__(self, url=None, username='', key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10):
        self._conn = HTTPClient(url, username, key, timeout, adapter, pool_size=pool_size)
        self._read_consistency = read_consistency

    def create_database(self, database_name: str, timeout: Optional[float] = None) -> Database:
        """Creates a database.

        :param database_name: The name of the database. A database name can only include
        numbers, letters, and underscores, and must not begin with a letter, and length 
        must between 1 and 128
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return Database object
        :rtype Database 
        """
        db = Database(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        db.create_database(timeout=timeout)
        return db

    def create_ai_database(self, database_name: str, timeout: Optional[float] = None) -> AIDatabase:
        """Creates an AI doc database.

        :param database_name: The name of the database. A database name can only include
        numbers, letters, and underscores, and must not begin with a letter, and length
        must between 1 and 128
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return Database object
        :rtype Database
        """
        db = AIDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        db.create_database(timeout=timeout)
        return db

    def drop_database(self, database_name: str, timeout: Optional[float] = None):
        """Delete a database.

        :param database_name: The name of the database to delete.
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
        """
        db = Database(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        return db.drop_database(timeout=timeout)

    def drop_ai_database(self, database_name: str, timeout: Optional[float] = None):
        """Delete an AI doc database.

        :param database_name: The name of the database to delete.
        :type  database_name: str

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float
        """
        db = AIDatabase(conn=self._conn, name=database_name, read_consistency=self._read_consistency)
        return db.drop_database(timeout=timeout)

    def list_databases(self, timeout: Optional[float] = None) -> List[Database]:
        """Get database list.

        :param timeout: An optional duration of time in seconds to allow for the request. When timeout
                        is set to None, will use the connect timeout.
        :type  timeout: float

        :return: The database name list
        :rtype: list[str]
        """
        db = Database(conn=self._conn, read_consistency=self._read_consistency)
        return db.list_databases(timeout=timeout)

    def database(self, database: str) -> Union[Database, AIDatabase]:
        """Get database list.

        :param database_name: The name of the database to delete.
        :type  database_name: str

        :return Database object
        :rtype Database 
        """
        for db in self.list_databases():
            if db.database_name == database:
                return db
        raise exceptions.ParamError(message='Database not exist: {}'.format(database))

    def close(self):
        """Close the connect session.

        :param database_name: The name of the database to delete.
        :type  database_name: str

        :return Database object
        :rtype Database 
        """
        if self._conn:
            self._conn.close()
            self._conn = None

    def upsert(self,
               database_name: str,
               collection_name: str,
               documents: List[Union[Document, Dict]],
               timeout: Optional[float] = None,
               build_index: bool = True,
               **kwargs):
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).upsert(
            documents=documents,
            timeout=timeout,
            build_index=build_index,
            **kwargs
        )

    def delete(self,
               database_name: str,
               collection_name: str,
               document_ids: List[str] = None,
               filter: Filter = None,
               timeout: Optional[float] = None):
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).delete(
            document_ids=document_ids,
            filter=filter,
            timeout=timeout,
        )

    def update(self,
               database_name: str,
               collection_name: str,
               data: Union[Document, Dict],
               filter: Optional[Filter] = None,
               document_ids: Optional[List[str]] = None,
               timeout: Optional[float] = None):
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).update(
            data=data,
            filter=filter,
            document_ids=document_ids,
            timeout=timeout,
        )

    def query(self,
              database_name: str,
              collection_name: str,
              document_ids: Optional[List] = None,
              retrieve_vector: bool = False,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              filter: Optional[Filter] = None,
              output_fields: Optional[List[str]] = None,
              timeout: Optional[float] = None,
              ) -> List[Dict]:
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).query(
            document_ids=document_ids,
            retrieve_vector=retrieve_vector,
            limit=limit,
            offset=offset,
            filter=filter,
            output_fields=output_fields,
            timeout=timeout,
        )

    def search(self,
               database_name: str,
               collection_name: str,
               vectors: List[List[float]],
               filter: Filter = None,
               params=None,
               retrieve_vector: bool = False,
               limit: int = 10,
               output_fields: Optional[List[str]] = None,
               timeout: Optional[float] = None,
               ) -> List[List[Dict]]:
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).search(
            vectors=vectors,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )

    def search_by_id(self,
                     database_name: str,
                     collection_name: str,
                     document_ids: List[str],
                     filter: Filter = None,
                     params=None,
                     retrieve_vector: bool = False,
                     limit: int = 10,
                     output_fields: Optional[List[str]] = None,
                     timeout: Optional[float] = None,
                     ) -> List[List[Dict]]:
        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).searchById(
            document_ids=document_ids,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            timeout=timeout,
            output_fields=output_fields,
        )

    def search_by_text(self,
                       database_name: str,
                       collection_name: str,
                       embedding_items: List[str],
                       filter: Filter = None,
                       params=None,
                       retrieve_vector: bool = False,
                       limit: int = 10,
                       output_fields: Optional[List[str]] = None,
                       timeout: Optional[float] = None,
                       ) -> Dict[str, Any]:

        return Collection(
            db=Database(conn=self._conn, name=database_name),
            name=collection_name,
            read_consistency=self._read_consistency,
        ).searchByText(
            embeddingItems=embedding_items,
            filter=filter,
            params=params,
            retrieve_vector=retrieve_vector,
            limit=limit,
            output_fields=output_fields,
            timeout=timeout,
        )
