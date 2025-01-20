from typing import Union, List

from tcvectordb.client.httpclient import HTTPClient


def create_user(conn: HTTPClient,
                user: str,
                password: str) -> dict:
    """Create a user.

    Args:
        conn (HTTPClient): Http client
        user (str): The username to create.
        password (str): The password of user.

    Returns:
        dict: The API returns a code and msg. For example:
       {
         "code": 0,
         "msg": "operation success"
       }
    """
    body = {
        'user': user,
        'password': password,
    }
    res = conn.post('/user/create', body)
    return res.data()


def drop_user(conn: HTTPClient,
              user: str) -> dict:
    """Drop a user.

    Args:
        conn (HTTPClient): Http client
        user (str): The username to create.

    Returns:
        dict: The API returns a code and msg. For example:
       {
         "code": 0,
         "msg": "operation success"
       }
    """
    body = {
        'user': user,
    }
    res = conn.post('/user/drop', body)
    return res.data()


def describe_user(conn: HTTPClient,
                  user: str) -> dict:
    """Get a user info.

    Args:
        conn (HTTPClient): Http client
        user (str): Username to get.

    Returns:
        dict: User info contains privileges. For example:
       {
          "user": "test_user",
          "createTime": "2024-10-01 00:00:00",
          "privileges": [
            {
              "resource": "db0.*",
              "actions": ["read"]
            }
          ]
        }
    """
    body = {
        'user': user,
    }
    res = conn.post('/user/describe', body)
    return res.data()


def user_list(conn: HTTPClient) -> List[dict]:
    """Get all users under the instance.

    Args:
        conn (HTTPClient): Http client

    Returns:
        dict: User info list. For example:
        [
          {
            "user": "test_user",
            "createTime": "2024-10-01 00:00:00",
            "privileges": [
              {
                "resource": "db0.*",
                "actions": ["read"]
              }
            ]
          }
       ]
    """
    res = conn.post('/user/list', {})
    return res.data().get('users', [])


def change_password(conn: HTTPClient,
                    user: str,
                    password: str) -> dict:
    """Change password for user.

    Args:
        conn (HTTPClient): Http client
        user (str): The user to change password.
        password (str): New password of the user.

    Returns:
        dict: The API returns a code and msg. For example:
       {
         "code": 0,
         "msg": "operation success"
       }
    """
    body = {
        'user': user,
        'password': password,
    }
    res = conn.post('/user/changePassword', body)
    return res.data()


def grant_to_user(conn: HTTPClient,
                  user: str,
                  privileges: Union[dict, List[dict]]) -> dict:
    """Grant permission for user.

    Args:
        conn (HTTPClient): Http client
        user (str): The user to grant permission.
        privileges (str): The privileges to grant. For example:
        {
          "resource": "db0.*",
          "actions": ["read"]
        }

    Returns:
        dict: The API returns a code and msg. For example:
       {
         "code": 0,
         "msg": "operation success"
       }
    """
    privileges = privileges if isinstance(privileges, list) else [privileges]
    body = {
        'user': user,
        'privileges': privileges,
    }
    res = conn.post('/user/grant', body)
    return res.data()


def revoke_from_user(conn: HTTPClient,
                     user: str,
                     privileges: Union[dict, List[dict]]) -> dict:
    """Revoke permission for user.

    Args:
        conn (HTTPClient): Http client
        user (str): The user to grant permission.
        privileges (str): The privilege to revoke. For example:
        {
          "resource": "db0.*",
          "actions": ["read"]
        }

    Returns:
        dict: The API returns a code and msg. For example:
       {
         "code": 0,
         "msg": "operation success"
       }
    """
    privileges = privileges if isinstance(privileges, list) else [privileges]
    body = {
        'user': user,
        'privileges': privileges,
    }
    res = conn.post('/user/revoke', body)
    return res.data()
