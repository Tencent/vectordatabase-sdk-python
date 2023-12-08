from typing import List, Optional, Union
from requests.adapters import HTTPAdapter

from tcvectordb.model.enum import ReadConsistency

from .httpclient import HTTPClient
from tcvectordb.model.database import Database
from tcvectordb import exceptions
from tcvectordb.model.ai_database import AIDatabase


class VectorDBClient:
    """
    VectorDBClient create a http client session for database operate.
    """

    def __init__(self, url=None, username='', key='',
                 read_consistency: ReadConsistency = ReadConsistency.EVENTUAL_CONSISTENCY,
                 timeout=5,
                 adapter: HTTPAdapter = None):
        self._conn = HTTPClient(url, username, key, timeout, adapter)
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
