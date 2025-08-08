import unittest
from unittest import mock

from tcvectordb.client.httpclient import HTTPClient, Response
from tcvectordb.model.database import Database
from tcvectordb.model.enum import ReadConsistency
from tcvectordb import exceptions
from tcvectordb.model.collection import Collection


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Mock HTTP client
        self.conn = mock.Mock(spec=HTTPClient)
        self.db_name = "test_db"
        self.database = Database(conn=self.conn, name=self.db_name)
        
        # Mock response for successful operations
        self.success_response = mock.Mock()
        self.success_response.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": {}
        }
        
        # Mock response for database list
        self.db_list_response = mock.Mock()
        self.db_list_response.json.return_value = {
            "code": 0,
            "msg": "success",
            "data": [
                {"database": "db1", "dbType": "BASE_DB", "count": 5},
                {"database": "db2", "dbType": "AI_DB", "count": 3}
            ]
        }

    def test_create_database_success(self):
        """Test successful database creation"""
        self.conn.post.return_value = Response("", self.success_response)
        
        # Test with database name in constructor
        db = Database(conn=self.conn, name=self.db_name)
        result = db.create_database()
        
        self.conn.post.assert_called_once_with(
            '/database/create',
            {'database': self.db_name},
            None
        )
        self.assertEqual(result.database_name, self.db_name)
    
    def test_create_database_with_name_param(self):
        """Test database creation with name parameter"""
        self.conn.post.return_value = Response("", self.success_response)
        db_name_param = "another_db"
        
        result = self.database.create_database(database_name=db_name_param)
        
        self.conn.post.assert_called_once_with(
            '/database/create',
            {'database': db_name_param},
            None
        )
        self.assertEqual(result.database_name, db_name_param)
    
    def test_create_database_no_connection(self):
        """Test database creation without connection"""
        db = Database(conn=None, name=self.db_name)
        with self.assertRaises(exceptions.NoConnectError):
            db.create_database()
    
    def test_create_database_no_name(self):
        """Test database creation without providing a name"""
        db = Database(conn=self.conn, name="")
        with self.assertRaises(exceptions.ParamError):
            db.create_database()
    
    def test_drop_database_success(self):
        """Test successful database deletion"""
        self.conn.post.return_value = Response("", self.success_response)
        
        result = self.database.drop_database()
        
        self.conn.post.assert_called_once_with(
            '/database/drop',
            {'database': self.db_name},
            None
        )
        self.assertEqual(result, self.success_response.json.return_value)
    
    def test_drop_nonexistent_database(self):
        """Test dropping a non-existent database"""
        error_response = mock.Mock()
        error_response.json.return_value = {
            "code": 0,
            "msg": "database not exist"
        }
        self.conn.post.return_value = Response("", error_response)
        
        result = self.database.drop_database(database_name="nonexistent_db")
        self.assertEqual(result, error_response.json.return_value)


if __name__ == '__main__':
    unittest.main()