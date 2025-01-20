# example for user api
import tcvectordb


vdb_url = "http://10.x.x.x"
vdb_key = "xB2i************************************"
db_name = "python-sdk-test-permission"


# tcvectordb.debug.DebugEnable = True

# create VectorDBClient
vdb_client = tcvectordb.RPCVectorDBClient(url=vdb_url,
                                          key=vdb_key,
                                          username='root',
                                          )

# create Database
vdb_client.create_database_if_not_exists(database_name=db_name)

try:
    vdb_client.drop_user(user='zhangsan')
except Exception as e:
    pass

# create user
print('\ncreate user zhangsan:')
print(vdb_client.create_user(user='zhangsan', password='0dd8e8b3d674'))

# describe user
print('\ndescribe user zhangsan:')
print(vdb_client.describe_user(user='zhangsan'))

# change password
print('\nchange zhangsan\'s password:')
print(vdb_client.change_password(user='zhangsan', password='dd8e8b3d6740'))
print('\ndescribe user zhangsan:')
print(vdb_client.describe_user(user='zhangsan'))

# grant permission
print('\ngrant permission for zhangsan')
print(vdb_client.grant_to_user(user='zhangsan',
                               privileges=[
                                   {
                                       "resource": "python-sdk-test-permission.*",
                                       "actions": ["read"]
                                   },
                                   {
                                       "resource": "python-sdk-test-permission.*",
                                       "actions": ["readWrite"]
                                   },
                               ]))
print('\ndescribe user zhangsan:')
print(vdb_client.describe_user(user='zhangsan'))

# revoke permission
print('\nrevoke permission for zhangsan')
print(vdb_client.revoke_from_user(user='zhangsan',
                                  privileges={
                                      "resource": "python-sdk-test-permission.*",
                                      "actions": ["read"]
                                  }))
print('\ndescribe user zhangsan:')
print(vdb_client.describe_user(user='zhangsan'))

# drop user
print('\ndrop user zhangsan:')
print(vdb_client.drop_user(user='zhangsan'))
# list user
print('\nlist users:')
print(vdb_client.user_list())

# clear env
vdb_client.drop_database(db_name)
vdb_client.close()
