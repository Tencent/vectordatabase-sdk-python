# Changelog

## 1.6.4
* fix: Keep using alias to access the interface within the Collection object.


## 1.6.3
* feat: `RPCVectorDBClient` support upload file to a `BASE_DB`.


## 1.6.2
* feat: Support `Json` FieldType.
* feat: Added support for automatic ID generation. Set `auto_id='uuid'` to use UUID for generating IDs.
* feat: Support upload file to a `BASE_DB`.


## 1.6.1
* feat: Add `set_stopwords` api.
* fix: Use HasField to determine the type of gRPC oneof field.


## 1.6.0
* feat: Support the user interface to grant or revoke privileges.
* feat: Support to sort the data by the sort rules firstly, when quering documents.
* feat: Support for using an `indexes` array to replace `Index` object when creating Collection.
* feat: Copy all interfaces to be directly used in Client.
* fix: Add `()` to previous expressions in `Filter` because `and` has higher precedence than `or`.


## 1.5.1
* refactor: Using ik stopwords as default stopwords file.


## 1.5.0
* feat: Support binary vector.
* feat: Support to return documents' count when using `count` function.
* feat: Support to delete documents with limit.
* feat: Add params `terminate_after` and `cutoff_frequency`, when hybrid search.
* feat: Support to hybrid search by text in embedding collection.
* feat: Support to modify vector indexes.
* feat: Support search `radius` for searching in collection.
* feat: Support full index mode to index all scalar fields.
 

## 1.4.10 
* feat: Support for model-based PDF document splitting.
* fix: Create array fields must specify `fieldElementType`.
* feat: Enhancing comments.


## 1.4.9
* fix: fix filter use str None.


## 1.4.8
* feat: Support `add_index` interface.
* feat: `RPCVectorDBClient` search and query can return pb object `olama_pb2.Document` directly.


## 1.4.7
* feat: `RPCVectorDBClient` no longer inherits HTTP interface methods.


## 1.4.6
* feat: Add `ttl_config` to automatically expire and delete documents in Collections after a specified period. 
* feat: Allow the `filter` parameter to accept string types expression directly.
* feat: Allow the `vector` parameter to accept NumPy types directly.
* feat: Display helpful messages for network and authentication errors.


## 1.4.5
* feat: Add `exists_db` `create_database_if_not_exists` `exists_collection` and `create_collection_if_not_exists` api.


## 1.4.4
* feat: `hybrid_search` api support single ann and single match.


## 1.4.3
* feat: Add a new `SparseIndex` object to replace `VectorIndex` when create a sparse index.


## 1.4.2
* fix: search use old grpc definition.


## 1.4.1
* feat: Add proxies to `VectorDBClient`.


## 1.4.0
* feat: Add bm25 tools: `tcvdb_text`
* feat: Supporting `SparseVector` index type and `hybrid_search` interfaces.


## 1.3.13
* feat: Support `chunk_splitter` expressions when parsing of Word document.


## 1.3.12
* fix: Remove the use of deepcopy during the conversion from document to pb objects.


## 1.3.11
* feat: Move the DML interfaces to be directly used in Client.


## 1.3.10
* feat: Add AI suite interfaces to `RPCVectorDBClient`.


## 1.3.9
* feat: And `shard` and `replicas` parameters when create CollectionView.


## 1.3.8
* feat: Return the `document_count` `alias` `index_status` for `Collection`.
* fix: Add `()` to follow expressions in Filter for And, Or, and AndNot operations.


## 1.3.7
* feat: Return the `create_time` for `Collection` and the `indexed_count` for `VectorIndex`.


## 1.3.6
* fix: Remove the `channel_ready_check` functionality from `RPCVectorDBClient`.


## 1.3.5
* feat: Add new parameters expected_file_num and average_file_size to `CollectionView` for optimizing shard number.


## 1.3.4
* feat: Add a close method to the Client to close the connection.
* fix: Remove `json.dumps` usage in Debug to prevent performance issues caused by fewer API calls.


## 1.3.3
* feat: Added the `RPCVectorDBClient`, which provides a faster Grpc interface.


## 1.3.2
* fix: The directory `tcvectordb/asyncapi/model/` has been converted into a module.


## 1.3.1
* feat: Added the `AsyncVectorDBClient`, which provides asynchronous interfaces.


## 1.3.0
* feat: The AI Suite now supports PDF, PPT, and Word documents.


## 1.2.0
* feat: Added the get_chunks interface to retrieve all chunks in the AI Suite.
* feat: Added the `chunk_splitter` parse parameter, a regular expression used to split chunks in the AI Suite.


## 1.1.0
* refactor: Added AI suite support for directly upload files, enabling rapid construction of exclusive knowledge bases.


## 1.0.4
* refactor: Added a *model_name* parameter to the `Embedding` class to replace the previous Enum parameter. This change improves compatibility by supporting a broader range of models.


## 1.0.3
* feat: Added the `IVFSQ4Params` and `IVFSQ16Params` classes.


## 1.0.2
* fix: Enhanced the support for the `In` expression in the `Filter` component to handle both string and numeric data types.


## 1.0.1
* feat: Supports passing text to the server for embedding generation.
* feat: Added alias functionality to reference collections.
* feat: Added support for the following IVF (Inverted File Index) index types: IVF_FLAT IVF_PQ IVF_SQ4 IVF_SQ8 IVF_SQ16.
* feat: Added the `truncate_collection` interface to clear all documents within a collection.
* feat: Added the `read_consistency` parameter to control the consistency level for read operations.


## 0.0.2
* feat: Supports DDL and DML functionalities.
