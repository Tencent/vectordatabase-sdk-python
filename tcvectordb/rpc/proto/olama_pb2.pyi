from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShardDataState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SHARD_INDEX_READY: _ClassVar[ShardDataState]
    SHARD_INDEX_TRAINING: _ClassVar[ShardDataState]
    SHARD_INDEX_BUILDING: _ClassVar[ShardDataState]
    SHARD_INDEX_FAILED: _ClassVar[ShardDataState]

class HealthState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    HEALTH_GREEN: _ClassVar[HealthState]
    HEALTH_YELLOW: _ClassVar[HealthState]
    HEALTH_RED: _ClassVar[HealthState]

class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    BASE: _ClassVar[DataType]
    AI_DOC: _ClassVar[DataType]

class IndexMetricType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    INDEX_METRIC_INNER_PRODUCT: _ClassVar[IndexMetricType]
    INDEX_METRIC_L2: _ClassVar[IndexMetricType]
    INDEX_METRIC_COSINE: _ClassVar[IndexMetricType]
    INDEX_METRIC_HAMMING: _ClassVar[IndexMetricType]

class IndexEngineType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ENGINE_FAISS_VECTOR: _ClassVar[IndexEngineType]
    ENGINE_FAISS_BINARY: _ClassVar[IndexEngineType]
    ENGINE_HNSWLIB: _ClassVar[IndexEngineType]

class FieldType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    TYPE_STRING: _ClassVar[FieldType]
    TYPE_ARRAY: _ClassVar[FieldType]
    TYPE_UINT64: _ClassVar[FieldType]
    TYPE_JSON: _ClassVar[FieldType]

class FieldElementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ELEMENT_TYPE_STRING: _ClassVar[FieldElementType]
SHARD_INDEX_READY: ShardDataState
SHARD_INDEX_TRAINING: ShardDataState
SHARD_INDEX_BUILDING: ShardDataState
SHARD_INDEX_FAILED: ShardDataState
HEALTH_GREEN: HealthState
HEALTH_YELLOW: HealthState
HEALTH_RED: HealthState
BASE: DataType
AI_DOC: DataType
INDEX_METRIC_INNER_PRODUCT: IndexMetricType
INDEX_METRIC_L2: IndexMetricType
INDEX_METRIC_COSINE: IndexMetricType
INDEX_METRIC_HAMMING: IndexMetricType
ENGINE_FAISS_VECTOR: IndexEngineType
ENGINE_FAISS_BINARY: IndexEngineType
ENGINE_HNSWLIB: IndexEngineType
TYPE_STRING: FieldType
TYPE_ARRAY: FieldType
TYPE_UINT64: FieldType
TYPE_JSON: FieldType
ELEMENT_TYPE_STRING: FieldElementType

class Document(_message.Message):
    __slots__ = ["id", "vector", "score", "fields", "index_id", "from_peer", "shard_idx", "vector_offset", "doc_info", "sparse_vector", "data_expr"]
    class FieldsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Field
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Field, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    INDEX_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_PEER_FIELD_NUMBER: _ClassVar[int]
    SHARD_IDX_FIELD_NUMBER: _ClassVar[int]
    VECTOR_OFFSET_FIELD_NUMBER: _ClassVar[int]
    DOC_INFO_FIELD_NUMBER: _ClassVar[int]
    SPARSE_VECTOR_FIELD_NUMBER: _ClassVar[int]
    DATA_EXPR_FIELD_NUMBER: _ClassVar[int]
    id: str
    vector: _containers.RepeatedScalarFieldContainer[float]
    score: float
    fields: _containers.MessageMap[str, Field]
    index_id: int
    from_peer: str
    shard_idx: int
    vector_offset: int
    doc_info: bytes
    sparse_vector: _containers.RepeatedCompositeFieldContainer[SparseVecItem]
    data_expr: str
    def __init__(self, id: _Optional[str] = ..., vector: _Optional[_Iterable[float]] = ..., score: _Optional[float] = ..., fields: _Optional[_Mapping[str, Field]] = ..., index_id: _Optional[int] = ..., from_peer: _Optional[str] = ..., shard_idx: _Optional[int] = ..., vector_offset: _Optional[int] = ..., doc_info: _Optional[bytes] = ..., sparse_vector: _Optional[_Iterable[_Union[SparseVecItem, _Mapping]]] = ..., data_expr: _Optional[str] = ...) -> None: ...

class Field(_message.Message):
    __slots__ = ["val_str", "val_u64", "val_double", "val_str_arr", "val_json"]
    class StringArray(_message.Message):
        __slots__ = ["str_arr"]
        STR_ARR_FIELD_NUMBER: _ClassVar[int]
        str_arr: _containers.RepeatedScalarFieldContainer[bytes]
        def __init__(self, str_arr: _Optional[_Iterable[bytes]] = ...) -> None: ...
    VAL_STR_FIELD_NUMBER: _ClassVar[int]
    VAL_U64_FIELD_NUMBER: _ClassVar[int]
    VAL_DOUBLE_FIELD_NUMBER: _ClassVar[int]
    VAL_STR_ARR_FIELD_NUMBER: _ClassVar[int]
    VAL_JSON_FIELD_NUMBER: _ClassVar[int]
    val_str: bytes
    val_u64: int
    val_double: float
    val_str_arr: Field.StringArray
    val_json: bytes
    def __init__(self, val_str: _Optional[bytes] = ..., val_u64: _Optional[int] = ..., val_double: _Optional[float] = ..., val_str_arr: _Optional[_Union[Field.StringArray, _Mapping]] = ..., val_json: _Optional[bytes] = ...) -> None: ...

class SparseVecItem(_message.Message):
    __slots__ = ["term_id", "score"]
    TERM_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    term_id: int
    score: float
    def __init__(self, term_id: _Optional[int] = ..., score: _Optional[float] = ...) -> None: ...

class ShardState(_message.Message):
    __slots__ = ["data_state", "estimate_index_mem_size", "snapshoting", "last_applied_index", "last_applied_term", "id_seed", "added_items", "data_state_change_time", "last_snapshot_time", "last_hnsw_resize_time", "last_index_rebuild_time"]
    DATA_STATE_FIELD_NUMBER: _ClassVar[int]
    ESTIMATE_INDEX_MEM_SIZE_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOTING_FIELD_NUMBER: _ClassVar[int]
    LAST_APPLIED_INDEX_FIELD_NUMBER: _ClassVar[int]
    LAST_APPLIED_TERM_FIELD_NUMBER: _ClassVar[int]
    ID_SEED_FIELD_NUMBER: _ClassVar[int]
    ADDED_ITEMS_FIELD_NUMBER: _ClassVar[int]
    DATA_STATE_CHANGE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_SNAPSHOT_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_HNSW_RESIZE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_INDEX_REBUILD_TIME_FIELD_NUMBER: _ClassVar[int]
    data_state: ShardDataState
    estimate_index_mem_size: int
    snapshoting: bool
    last_applied_index: int
    last_applied_term: int
    id_seed: int
    added_items: int
    data_state_change_time: int
    last_snapshot_time: int
    last_hnsw_resize_time: int
    last_index_rebuild_time: int
    def __init__(self, data_state: _Optional[_Union[ShardDataState, str]] = ..., estimate_index_mem_size: _Optional[int] = ..., snapshoting: bool = ..., last_applied_index: _Optional[int] = ..., last_applied_term: _Optional[int] = ..., id_seed: _Optional[int] = ..., added_items: _Optional[int] = ..., data_state_change_time: _Optional[int] = ..., last_snapshot_time: _Optional[int] = ..., last_hnsw_resize_time: _Optional[int] = ..., last_index_rebuild_time: _Optional[int] = ...) -> None: ...

class Shard(_message.Message):
    __slots__ = ["collection", "shard_idx", "is_leader", "following", "state", "nodes", "from_node", "version"]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    SHARD_IDX_FIELD_NUMBER: _ClassVar[int]
    IS_LEADER_FIELD_NUMBER: _ClassVar[int]
    FOLLOWING_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    FROM_NODE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    collection: str
    shard_idx: int
    is_leader: bool
    following: bool
    state: ShardState
    nodes: _containers.RepeatedScalarFieldContainer[str]
    from_node: str
    version: int
    def __init__(self, collection: _Optional[str] = ..., shard_idx: _Optional[int] = ..., is_leader: bool = ..., following: bool = ..., state: _Optional[_Union[ShardState, _Mapping]] = ..., nodes: _Optional[_Iterable[str]] = ..., from_node: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class AliasItem(_message.Message):
    __slots__ = ["alias", "collection"]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    alias: str
    collection: str
    def __init__(self, alias: _Optional[str] = ..., collection: _Optional[str] = ...) -> None: ...

class DatabaseItem(_message.Message):
    __slots__ = ["create_time", "db_type", "count"]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    DB_TYPE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    create_time: int
    db_type: DataType
    count: int
    def __init__(self, create_time: _Optional[int] = ..., db_type: _Optional[_Union[DataType, str]] = ..., count: _Optional[int] = ...) -> None: ...

class SnapshotRule(_message.Message):
    __slots__ = ["period_secs", "changed_docs"]
    PERIOD_SECS_FIELD_NUMBER: _ClassVar[int]
    CHANGED_DOCS_FIELD_NUMBER: _ClassVar[int]
    period_secs: int
    changed_docs: int
    def __init__(self, period_secs: _Optional[int] = ..., changed_docs: _Optional[int] = ...) -> None: ...

class EmbeddingParams(_message.Message):
    __slots__ = ["field", "vector_field", "model_name"]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    field: str
    vector_field: str
    model_name: str
    def __init__(self, field: _Optional[str] = ..., vector_field: _Optional[str] = ..., model_name: _Optional[str] = ...) -> None: ...

class CollectionConf(_message.Message):
    __slots__ = ["database", "collection", "description", "number_of_shards", "number_of_replicas", "dimension", "metric", "nprobe", "snapshot_rules", "engine", "model_desc", "field_metas", "options", "nlist", "embedding_params", "data_type", "version", "ttlConfig"]
    class FieldMetasEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FieldMeta
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FieldMeta, _Mapping]] = ...) -> None: ...
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_SHARDS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    NPROBE_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_RULES_FIELD_NUMBER: _ClassVar[int]
    ENGINE_FIELD_NUMBER: _ClassVar[int]
    MODEL_DESC_FIELD_NUMBER: _ClassVar[int]
    FIELD_METAS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    NLIST_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_PARAMS_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TTLCONFIG_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    description: str
    number_of_shards: int
    number_of_replicas: int
    dimension: int
    metric: IndexMetricType
    nprobe: int
    snapshot_rules: _containers.RepeatedCompositeFieldContainer[SnapshotRule]
    engine: IndexEngineType
    model_desc: str
    field_metas: _containers.MessageMap[str, FieldMeta]
    options: _containers.ScalarMap[str, str]
    nlist: int
    embedding_params: EmbeddingParams
    data_type: DataType
    version: int
    ttlConfig: TTLConfig
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., description: _Optional[str] = ..., number_of_shards: _Optional[int] = ..., number_of_replicas: _Optional[int] = ..., dimension: _Optional[int] = ..., metric: _Optional[_Union[IndexMetricType, str]] = ..., nprobe: _Optional[int] = ..., snapshot_rules: _Optional[_Iterable[_Union[SnapshotRule, _Mapping]]] = ..., engine: _Optional[_Union[IndexEngineType, str]] = ..., model_desc: _Optional[str] = ..., field_metas: _Optional[_Mapping[str, FieldMeta]] = ..., options: _Optional[_Mapping[str, str]] = ..., nlist: _Optional[int] = ..., embedding_params: _Optional[_Union[EmbeddingParams, _Mapping]] = ..., data_type: _Optional[_Union[DataType, str]] = ..., version: _Optional[int] = ..., ttlConfig: _Optional[_Union[TTLConfig, _Mapping]] = ...) -> None: ...

class FieldMeta(_message.Message):
    __slots__ = ["field_type", "field_element_type"]
    FIELD_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIELD_ELEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    field_type: FieldType
    field_element_type: FieldElementType
    def __init__(self, field_type: _Optional[_Union[FieldType, str]] = ..., field_element_type: _Optional[_Union[FieldElementType, str]] = ...) -> None: ...

class ShardConf(_message.Message):
    __slots__ = ["collection", "shard_idx", "conf", "nodes"]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    SHARD_IDX_FIELD_NUMBER: _ClassVar[int]
    CONF_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    collection: str
    shard_idx: int
    conf: CollectionConf
    nodes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, collection: _Optional[str] = ..., shard_idx: _Optional[int] = ..., conf: _Optional[_Union[CollectionConf, _Mapping]] = ..., nodes: _Optional[_Iterable[str]] = ...) -> None: ...

class TTLConfig(_message.Message):
    __slots__ = ["enable", "timeField"]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    TIMEFIELD_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    timeField: str
    def __init__(self, enable: bool = ..., timeField: _Optional[str] = ...) -> None: ...

class ShardCollectionState(_message.Message):
    __slots__ = ["shard_idx", "leader", "node_peers", "allocate_start_ms", "allocate_stop_ms", "leader_ms", "allocating", "shards", "creating", "removing"]
    SHARD_IDX_FIELD_NUMBER: _ClassVar[int]
    LEADER_FIELD_NUMBER: _ClassVar[int]
    NODE_PEERS_FIELD_NUMBER: _ClassVar[int]
    ALLOCATE_START_MS_FIELD_NUMBER: _ClassVar[int]
    ALLOCATE_STOP_MS_FIELD_NUMBER: _ClassVar[int]
    LEADER_MS_FIELD_NUMBER: _ClassVar[int]
    ALLOCATING_FIELD_NUMBER: _ClassVar[int]
    SHARDS_FIELD_NUMBER: _ClassVar[int]
    CREATING_FIELD_NUMBER: _ClassVar[int]
    REMOVING_FIELD_NUMBER: _ClassVar[int]
    shard_idx: int
    leader: str
    node_peers: _containers.RepeatedScalarFieldContainer[str]
    allocate_start_ms: int
    allocate_stop_ms: int
    leader_ms: int
    allocating: bool
    shards: _containers.RepeatedCompositeFieldContainer[Shard]
    creating: bool
    removing: bool
    def __init__(self, shard_idx: _Optional[int] = ..., leader: _Optional[str] = ..., node_peers: _Optional[_Iterable[str]] = ..., allocate_start_ms: _Optional[int] = ..., allocate_stop_ms: _Optional[int] = ..., leader_ms: _Optional[int] = ..., allocating: bool = ..., shards: _Optional[_Iterable[_Union[Shard, _Mapping]]] = ..., creating: bool = ..., removing: bool = ...) -> None: ...

class CollectionState(_message.Message):
    __slots__ = ["collection", "conf", "shards", "size", "create_time", "req", "status", "index_state"]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    CONF_FIELD_NUMBER: _ClassVar[int]
    SHARDS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    REQ_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INDEX_STATE_FIELD_NUMBER: _ClassVar[int]
    collection: str
    conf: CollectionConf
    shards: _containers.RepeatedCompositeFieldContainer[ShardCollectionState]
    size: int
    create_time: int
    req: CreateCollectionRequest
    status: HealthState
    index_state: ShardDataState
    def __init__(self, collection: _Optional[str] = ..., conf: _Optional[_Union[CollectionConf, _Mapping]] = ..., shards: _Optional[_Iterable[_Union[ShardCollectionState, _Mapping]]] = ..., size: _Optional[int] = ..., create_time: _Optional[int] = ..., req: _Optional[_Union[CreateCollectionRequest, _Mapping]] = ..., status: _Optional[_Union[HealthState, str]] = ..., index_state: _Optional[_Union[ShardDataState, str]] = ...) -> None: ...

class AddAliasRequest(_message.Message):
    __slots__ = ["database", "collection", "alias"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    alias: str
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., alias: _Optional[str] = ...) -> None: ...

class RemoveAliasRequest(_message.Message):
    __slots__ = ["database", "alias"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    database: str
    alias: str
    def __init__(self, database: _Optional[str] = ..., alias: _Optional[str] = ...) -> None: ...

class UpdateAliasResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedCount"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedCount: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedCount: _Optional[int] = ...) -> None: ...

class GetAliasRequest(_message.Message):
    __slots__ = ["database", "alias"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    database: str
    alias: str
    def __init__(self, database: _Optional[str] = ..., alias: _Optional[str] = ...) -> None: ...

class GetAliasResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "aliases"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    ALIASES_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    aliases: _containers.RepeatedCompositeFieldContainer[AliasItem]
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., aliases: _Optional[_Iterable[_Union[AliasItem, _Mapping]]] = ...) -> None: ...

class GetNodeInfoRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetNodeInfoResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "node_infos"]
    class NodeInfosEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    NODE_INFOS_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    node_infos: _containers.ScalarMap[str, str]
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., node_infos: _Optional[_Mapping[str, str]] = ...) -> None: ...

class DescribeCollectionRequest(_message.Message):
    __slots__ = ["database", "collection", "transfer"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    transfer: bool
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., transfer: bool = ...) -> None: ...

class DescribeCollectionResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "collection", "state"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    collection: CreateCollectionRequest
    state: CollectionState
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., collection: _Optional[_Union[CreateCollectionRequest, _Mapping]] = ..., state: _Optional[_Union[CollectionState, _Mapping]] = ...) -> None: ...

class ListCollectionsRequest(_message.Message):
    __slots__ = ["database", "transfer"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_FIELD_NUMBER: _ClassVar[int]
    database: str
    transfer: bool
    def __init__(self, database: _Optional[str] = ..., transfer: bool = ...) -> None: ...

class ListCollectionsResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "collections", "states"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    COLLECTIONS_FIELD_NUMBER: _ClassVar[int]
    STATES_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    collections: _containers.RepeatedCompositeFieldContainer[CreateCollectionRequest]
    states: _containers.RepeatedCompositeFieldContainer[CollectionState]
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., collections: _Optional[_Iterable[_Union[CreateCollectionRequest, _Mapping]]] = ..., states: _Optional[_Iterable[_Union[CollectionState, _Mapping]]] = ...) -> None: ...

class IndexParams(_message.Message):
    __slots__ = ["M", "efConstruction", "nprobe", "nlist"]
    M_FIELD_NUMBER: _ClassVar[int]
    EFCONSTRUCTION_FIELD_NUMBER: _ClassVar[int]
    NPROBE_FIELD_NUMBER: _ClassVar[int]
    NLIST_FIELD_NUMBER: _ClassVar[int]
    M: int
    efConstruction: int
    nprobe: int
    nlist: int
    def __init__(self, M: _Optional[int] = ..., efConstruction: _Optional[int] = ..., nprobe: _Optional[int] = ..., nlist: _Optional[int] = ...) -> None: ...

class IndexColumn(_message.Message):
    __slots__ = ["fieldName", "fieldType", "indexType", "dimension", "metricType", "params", "fieldElementType", "autoId"]
    FIELDNAME_FIELD_NUMBER: _ClassVar[int]
    FIELDTYPE_FIELD_NUMBER: _ClassVar[int]
    INDEXTYPE_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_FIELD_NUMBER: _ClassVar[int]
    METRICTYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    FIELDELEMENTTYPE_FIELD_NUMBER: _ClassVar[int]
    AUTOID_FIELD_NUMBER: _ClassVar[int]
    fieldName: str
    fieldType: str
    indexType: str
    dimension: int
    metricType: str
    params: IndexParams
    fieldElementType: str
    autoId: str
    def __init__(self, fieldName: _Optional[str] = ..., fieldType: _Optional[str] = ..., indexType: _Optional[str] = ..., dimension: _Optional[int] = ..., metricType: _Optional[str] = ..., params: _Optional[_Union[IndexParams, _Mapping]] = ..., fieldElementType: _Optional[str] = ..., autoId: _Optional[str] = ...) -> None: ...

class indexStatus(_message.Message):
    __slots__ = ["status", "progress", "startTime"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    status: str
    progress: str
    startTime: str
    def __init__(self, status: _Optional[str] = ..., progress: _Optional[str] = ..., startTime: _Optional[str] = ...) -> None: ...

class FilterIndexConfig(_message.Message):
    __slots__ = ["filterAll", "fieldsWithoutIndex", "maxStrLen"]
    FILTERALL_FIELD_NUMBER: _ClassVar[int]
    FIELDSWITHOUTINDEX_FIELD_NUMBER: _ClassVar[int]
    MAXSTRLEN_FIELD_NUMBER: _ClassVar[int]
    filterAll: bool
    fieldsWithoutIndex: _containers.RepeatedScalarFieldContainer[str]
    maxStrLen: int
    def __init__(self, filterAll: bool = ..., fieldsWithoutIndex: _Optional[_Iterable[str]] = ..., maxStrLen: _Optional[int] = ...) -> None: ...

class CreateCollectionRequest(_message.Message):
    __slots__ = ["database", "collection", "replicaNum", "shardNum", "size", "createTime", "description", "indexes", "indexStatus", "alias_list", "embeddingParams", "version", "ttlConfig", "filterIndexConfig", "document_count"]
    class IndexesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: IndexColumn
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[IndexColumn, _Mapping]] = ...) -> None: ...
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    REPLICANUM_FIELD_NUMBER: _ClassVar[int]
    SHARDNUM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CREATETIME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INDEXES_FIELD_NUMBER: _ClassVar[int]
    INDEXSTATUS_FIELD_NUMBER: _ClassVar[int]
    ALIAS_LIST_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGPARAMS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TTLCONFIG_FIELD_NUMBER: _ClassVar[int]
    FILTERINDEXCONFIG_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    replicaNum: int
    shardNum: int
    size: int
    createTime: str
    description: str
    indexes: _containers.MessageMap[str, IndexColumn]
    indexStatus: indexStatus
    alias_list: _containers.RepeatedScalarFieldContainer[str]
    embeddingParams: EmbeddingParams
    version: int
    ttlConfig: TTLConfig
    filterIndexConfig: FilterIndexConfig
    document_count: int
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., replicaNum: _Optional[int] = ..., shardNum: _Optional[int] = ..., size: _Optional[int] = ..., createTime: _Optional[str] = ..., description: _Optional[str] = ..., indexes: _Optional[_Mapping[str, IndexColumn]] = ..., indexStatus: _Optional[_Union[indexStatus, _Mapping]] = ..., alias_list: _Optional[_Iterable[str]] = ..., embeddingParams: _Optional[_Union[EmbeddingParams, _Mapping]] = ..., version: _Optional[int] = ..., ttlConfig: _Optional[_Union[TTLConfig, _Mapping]] = ..., filterIndexConfig: _Optional[_Union[FilterIndexConfig, _Mapping]] = ..., document_count: _Optional[int] = ...) -> None: ...

class CreateCollectionResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedCount"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedCount: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedCount: _Optional[int] = ...) -> None: ...

class DropCollectionRequest(_message.Message):
    __slots__ = ["database", "collection", "force", "without_alias"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    WITHOUT_ALIAS_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    force: bool
    without_alias: bool
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., force: bool = ..., without_alias: bool = ...) -> None: ...

class DropCollectionResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedCount"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedCount: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedCount: _Optional[int] = ...) -> None: ...

class TruncateCollectionRequest(_message.Message):
    __slots__ = ["database", "collection", "only_truncate_ann_index"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    ONLY_TRUNCATE_ANN_INDEX_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    only_truncate_ann_index: bool
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., only_truncate_ann_index: bool = ...) -> None: ...

class TruncateCollectionResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedCount"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedCount: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedCount: _Optional[int] = ...) -> None: ...

class RebuildIndexRequest(_message.Message):
    __slots__ = ["database", "collection", "dropBeforeRebuild", "throttle", "disable_train", "force_rebuild"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    DROPBEFOREREBUILD_FIELD_NUMBER: _ClassVar[int]
    THROTTLE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_TRAIN_FIELD_NUMBER: _ClassVar[int]
    FORCE_REBUILD_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    dropBeforeRebuild: bool
    throttle: int
    disable_train: bool
    force_rebuild: bool
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., dropBeforeRebuild: bool = ..., throttle: _Optional[int] = ..., disable_train: bool = ..., force_rebuild: bool = ...) -> None: ...

class RebuildIndexResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "task_ids"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., task_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UpsertRequest(_message.Message):
    __slots__ = ["database", "collection", "buildIndex", "documents", "buildIndexMode"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    BUILDINDEX_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    BUILDINDEXMODE_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    buildIndex: bool
    documents: _containers.RepeatedCompositeFieldContainer[Document]
    buildIndexMode: str
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., buildIndex: bool = ..., documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ..., buildIndexMode: _Optional[str] = ...) -> None: ...

class EmbeddingExtraInfo(_message.Message):
    __slots__ = ["token_used"]
    TOKEN_USED_FIELD_NUMBER: _ClassVar[int]
    token_used: int
    def __init__(self, token_used: _Optional[int] = ...) -> None: ...

class UpsertResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedCount", "warning", "embedding_extra_info"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    WARNING_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_EXTRA_INFO_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedCount: int
    warning: str
    embedding_extra_info: EmbeddingExtraInfo
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedCount: _Optional[int] = ..., warning: _Optional[str] = ..., embedding_extra_info: _Optional[_Union[EmbeddingExtraInfo, _Mapping]] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ["database", "collection", "query", "update"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    query: QueryCond
    update: Document
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., query: _Optional[_Union[QueryCond, _Mapping]] = ..., update: _Optional[_Union[Document, _Mapping]] = ...) -> None: ...

class UpdateResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedCount", "warning", "embedding_extra_info"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    WARNING_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_EXTRA_INFO_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedCount: int
    warning: str
    embedding_extra_info: EmbeddingExtraInfo
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedCount: _Optional[int] = ..., warning: _Optional[str] = ..., embedding_extra_info: _Optional[_Union[EmbeddingExtraInfo, _Mapping]] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ["database", "collection", "query"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    query: QueryCond
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., query: _Optional[_Union[QueryCond, _Mapping]] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedCount"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedCount: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedCount: _Optional[int] = ...) -> None: ...

class OrderRule(_message.Message):
    __slots__ = ["fieldName", "desc"]
    FIELDNAME_FIELD_NUMBER: _ClassVar[int]
    DESC_FIELD_NUMBER: _ClassVar[int]
    fieldName: str
    desc: bool
    def __init__(self, fieldName: _Optional[str] = ..., desc: bool = ...) -> None: ...

class QueryCond(_message.Message):
    __slots__ = ["documentIds", "indexIds", "retrieveVector", "filter", "limit", "offset", "outputFields", "retrieveSparseVector", "sort"]
    DOCUMENTIDS_FIELD_NUMBER: _ClassVar[int]
    INDEXIDS_FIELD_NUMBER: _ClassVar[int]
    RETRIEVEVECTOR_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    OUTPUTFIELDS_FIELD_NUMBER: _ClassVar[int]
    RETRIEVESPARSEVECTOR_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    documentIds: _containers.RepeatedScalarFieldContainer[str]
    indexIds: _containers.RepeatedScalarFieldContainer[int]
    retrieveVector: bool
    filter: str
    limit: int
    offset: int
    outputFields: _containers.RepeatedScalarFieldContainer[str]
    retrieveSparseVector: bool
    sort: _containers.RepeatedCompositeFieldContainer[OrderRule]
    def __init__(self, documentIds: _Optional[_Iterable[str]] = ..., indexIds: _Optional[_Iterable[int]] = ..., retrieveVector: bool = ..., filter: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., outputFields: _Optional[_Iterable[str]] = ..., retrieveSparseVector: bool = ..., sort: _Optional[_Iterable[_Union[OrderRule, _Mapping]]] = ...) -> None: ...

class QueryRequest(_message.Message):
    __slots__ = ["database", "collection", "query", "readConsistency"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    READCONSISTENCY_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    query: QueryCond
    readConsistency: str
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., query: _Optional[_Union[QueryCond, _Mapping]] = ..., readConsistency: _Optional[str] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "documents", "count"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    documents: _containers.RepeatedCompositeFieldContainer[Document]
    count: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class ExplainRequest(_message.Message):
    __slots__ = ["database", "collection", "query", "readConsistency"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    READCONSISTENCY_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    query: QueryCond
    readConsistency: str
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., query: _Optional[_Union[QueryCond, _Mapping]] = ..., readConsistency: _Optional[str] = ...) -> None: ...

class ExplainResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "affectedTable", "affectedCount"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDTABLE_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    affectedTable: _containers.RepeatedScalarFieldContainer[int]
    affectedCount: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., affectedTable: _Optional[_Iterable[int]] = ..., affectedCount: _Optional[int] = ...) -> None: ...

class CountRequest(_message.Message):
    __slots__ = ["database", "collection", "query"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    query: QueryCond
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., query: _Optional[_Union[QueryCond, _Mapping]] = ...) -> None: ...

class CountResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "count"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    count: int
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class SearchResult(_message.Message):
    __slots__ = ["documents"]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    documents: _containers.RepeatedCompositeFieldContainer[Document]
    def __init__(self, documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ...) -> None: ...

class SearchParams(_message.Message):
    __slots__ = ["nprobe", "ef", "radius"]
    NPROBE_FIELD_NUMBER: _ClassVar[int]
    EF_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    nprobe: int
    ef: int
    radius: float
    def __init__(self, nprobe: _Optional[int] = ..., ef: _Optional[int] = ..., radius: _Optional[float] = ...) -> None: ...

class VectorArray(_message.Message):
    __slots__ = ["vector"]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    vector: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, vector: _Optional[_Iterable[float]] = ...) -> None: ...

class AnnData(_message.Message):
    __slots__ = ["fieldName", "data", "documentIds", "params", "limit", "data_expr", "embeddingItems"]
    FIELDNAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTIDS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    DATA_EXPR_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGITEMS_FIELD_NUMBER: _ClassVar[int]
    fieldName: str
    data: _containers.RepeatedCompositeFieldContainer[VectorArray]
    documentIds: _containers.RepeatedScalarFieldContainer[str]
    params: SearchParams
    limit: int
    data_expr: _containers.RepeatedScalarFieldContainer[str]
    embeddingItems: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fieldName: _Optional[str] = ..., data: _Optional[_Iterable[_Union[VectorArray, _Mapping]]] = ..., documentIds: _Optional[_Iterable[str]] = ..., params: _Optional[_Union[SearchParams, _Mapping]] = ..., limit: _Optional[int] = ..., data_expr: _Optional[_Iterable[str]] = ..., embeddingItems: _Optional[_Iterable[str]] = ...) -> None: ...

class SparseVectorArray(_message.Message):
    __slots__ = ["sp_vector"]
    SP_VECTOR_FIELD_NUMBER: _ClassVar[int]
    sp_vector: _containers.RepeatedCompositeFieldContainer[SparseVecItem]
    def __init__(self, sp_vector: _Optional[_Iterable[_Union[SparseVecItem, _Mapping]]] = ...) -> None: ...

class SparseSearchParams(_message.Message):
    __slots__ = ["terminateAfter", "cutoffFrequency"]
    TERMINATEAFTER_FIELD_NUMBER: _ClassVar[int]
    CUTOFFFREQUENCY_FIELD_NUMBER: _ClassVar[int]
    terminateAfter: int
    cutoffFrequency: float
    def __init__(self, terminateAfter: _Optional[int] = ..., cutoffFrequency: _Optional[float] = ...) -> None: ...

class SparseData(_message.Message):
    __slots__ = ["fieldName", "data", "limit", "params"]
    FIELDNAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    fieldName: str
    data: _containers.RepeatedCompositeFieldContainer[SparseVectorArray]
    limit: int
    params: SparseSearchParams
    def __init__(self, fieldName: _Optional[str] = ..., data: _Optional[_Iterable[_Union[SparseVectorArray, _Mapping]]] = ..., limit: _Optional[int] = ..., params: _Optional[_Union[SparseSearchParams, _Mapping]] = ...) -> None: ...

class RerankParams(_message.Message):
    __slots__ = ["method", "weights", "rrf_k"]
    class WeightsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    METHOD_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    RRF_K_FIELD_NUMBER: _ClassVar[int]
    method: str
    weights: _containers.ScalarMap[str, float]
    rrf_k: int
    def __init__(self, method: _Optional[str] = ..., weights: _Optional[_Mapping[str, float]] = ..., rrf_k: _Optional[int] = ...) -> None: ...

class SearchCond(_message.Message):
    __slots__ = ["vectors", "documentIds", "params", "filter", "retrieveVector", "limit", "outputfields", "embeddingItems", "range", "ann", "sparse", "rerank_params", "retrieveSparseVector"]
    VECTORS_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTIDS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    RETRIEVEVECTOR_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTFIELDS_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGITEMS_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    SPARSE_FIELD_NUMBER: _ClassVar[int]
    RERANK_PARAMS_FIELD_NUMBER: _ClassVar[int]
    RETRIEVESPARSEVECTOR_FIELD_NUMBER: _ClassVar[int]
    vectors: _containers.RepeatedCompositeFieldContainer[VectorArray]
    documentIds: _containers.RepeatedScalarFieldContainer[str]
    params: SearchParams
    filter: str
    retrieveVector: bool
    limit: int
    outputfields: _containers.RepeatedScalarFieldContainer[str]
    embeddingItems: _containers.RepeatedScalarFieldContainer[str]
    range: bool
    ann: _containers.RepeatedCompositeFieldContainer[AnnData]
    sparse: _containers.RepeatedCompositeFieldContainer[SparseData]
    rerank_params: RerankParams
    retrieveSparseVector: bool
    def __init__(self, vectors: _Optional[_Iterable[_Union[VectorArray, _Mapping]]] = ..., documentIds: _Optional[_Iterable[str]] = ..., params: _Optional[_Union[SearchParams, _Mapping]] = ..., filter: _Optional[str] = ..., retrieveVector: bool = ..., limit: _Optional[int] = ..., outputfields: _Optional[_Iterable[str]] = ..., embeddingItems: _Optional[_Iterable[str]] = ..., range: bool = ..., ann: _Optional[_Iterable[_Union[AnnData, _Mapping]]] = ..., sparse: _Optional[_Iterable[_Union[SparseData, _Mapping]]] = ..., rerank_params: _Optional[_Union[RerankParams, _Mapping]] = ..., retrieveSparseVector: bool = ...) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ["database", "collection", "search", "readConsistency"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    READCONSISTENCY_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    search: SearchCond
    readConsistency: str
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., search: _Optional[_Union[SearchCond, _Mapping]] = ..., readConsistency: _Optional[str] = ...) -> None: ...

class ExposeDataUni(_message.Message):
    __slots__ = ["expose_name", "buffer"]
    EXPOSE_NAME_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    expose_name: str
    buffer: bytes
    def __init__(self, expose_name: _Optional[str] = ..., buffer: _Optional[bytes] = ...) -> None: ...

class ExposeData(_message.Message):
    __slots__ = ["expose_data_uni"]
    EXPOSE_DATA_UNI_FIELD_NUMBER: _ClassVar[int]
    expose_data_uni: _containers.RepeatedCompositeFieldContainer[ExposeDataUni]
    def __init__(self, expose_data_uni: _Optional[_Iterable[_Union[ExposeDataUni, _Mapping]]] = ...) -> None: ...

class Filter(_message.Message):
    __slots__ = ["expr", "radius", "size", "expose_data"]
    EXPR_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    EXPOSE_DATA_FIELD_NUMBER: _ClassVar[int]
    expr: str
    radius: float
    size: int
    expose_data: ExposeData
    def __init__(self, expr: _Optional[str] = ..., radius: _Optional[float] = ..., size: _Optional[int] = ..., expose_data: _Optional[_Union[ExposeData, _Mapping]] = ...) -> None: ...

class RoaringBinary(_message.Message):
    __slots__ = ["size", "data"]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    size: int
    data: bytes
    def __init__(self, size: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "results", "warning", "embedding_extra_info"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    WARNING_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_EXTRA_INFO_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    results: _containers.RepeatedCompositeFieldContainer[SearchResult]
    warning: str
    embedding_extra_info: EmbeddingExtraInfo
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., results: _Optional[_Iterable[_Union[SearchResult, _Mapping]]] = ..., warning: _Optional[str] = ..., embedding_extra_info: _Optional[_Union[EmbeddingExtraInfo, _Mapping]] = ...) -> None: ...

class SortCond(_message.Message):
    __slots__ = ["sort_vec", "sort_id", "ids"]
    SORT_VEC_FIELD_NUMBER: _ClassVar[int]
    SORT_ID_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    sort_vec: _containers.RepeatedScalarFieldContainer[float]
    sort_id: str
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sort_vec: _Optional[_Iterable[float]] = ..., sort_id: _Optional[str] = ..., ids: _Optional[_Iterable[str]] = ...) -> None: ...

class SortRequest(_message.Message):
    __slots__ = ["database", "collection", "shard_idx", "cond", "limit", "metric"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    SHARD_IDX_FIELD_NUMBER: _ClassVar[int]
    COND_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    shard_idx: int
    cond: SortCond
    limit: int
    metric: IndexMetricType
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., shard_idx: _Optional[int] = ..., cond: _Optional[_Union[SortCond, _Mapping]] = ..., limit: _Optional[int] = ..., metric: _Optional[_Union[IndexMetricType, str]] = ...) -> None: ...

class SortResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "documents", "invalid_conds"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    INVALID_CONDS_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    documents: _containers.RepeatedCompositeFieldContainer[Document]
    invalid_conds: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ..., invalid_conds: _Optional[_Iterable[str]] = ...) -> None: ...

class DatabaseRequest(_message.Message):
    __slots__ = ["database", "dbType"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    DBTYPE_FIELD_NUMBER: _ClassVar[int]
    database: str
    dbType: DataType
    def __init__(self, database: _Optional[str] = ..., dbType: _Optional[_Union[DataType, str]] = ...) -> None: ...

class DatabaseResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "databases", "affectedCount", "info"]
    class InfoEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: DatabaseItem
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[DatabaseItem, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    DATABASES_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDCOUNT_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    databases: _containers.RepeatedScalarFieldContainer[str]
    affectedCount: int
    info: _containers.MessageMap[str, DatabaseItem]
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., databases: _Optional[_Iterable[str]] = ..., affectedCount: _Optional[int] = ..., info: _Optional[_Mapping[str, DatabaseItem]] = ...) -> None: ...

class DescribeDatabaseRequest(_message.Message):
    __slots__ = ["database"]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    database: str
    def __init__(self, database: _Optional[str] = ...) -> None: ...

class DescribeDatabaseResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "database"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    database: DatabaseItem
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., database: _Optional[_Union[DatabaseItem, _Mapping]] = ...) -> None: ...

class GetVersionRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetVersionResponse(_message.Message):
    __slots__ = ["timestamp", "kernal_version"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    KERNAL_VERSION_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    kernal_version: int
    def __init__(self, timestamp: _Optional[int] = ..., kernal_version: _Optional[int] = ...) -> None: ...

class ModifyVectorIndexRequest(_message.Message):
    __slots__ = ["database", "collection", "vectorIndexes", "rebuildRules"]
    class VectorIndexesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: IndexColumn
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[IndexColumn, _Mapping]] = ...) -> None: ...
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    VECTORINDEXES_FIELD_NUMBER: _ClassVar[int]
    REBUILDRULES_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    vectorIndexes: _containers.MessageMap[str, IndexColumn]
    rebuildRules: RebuildIndexRequest
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., vectorIndexes: _Optional[_Mapping[str, IndexColumn]] = ..., rebuildRules: _Optional[_Union[RebuildIndexRequest, _Mapping]] = ...) -> None: ...

class ModifyVectorIndexResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ...) -> None: ...

class AddIndexRequest(_message.Message):
    __slots__ = ["database", "collection", "indexes", "buildExistedData"]
    class IndexesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: IndexColumn
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[IndexColumn, _Mapping]] = ...) -> None: ...
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    INDEXES_FIELD_NUMBER: _ClassVar[int]
    BUILDEXISTEDDATA_FIELD_NUMBER: _ClassVar[int]
    database: str
    collection: str
    indexes: _containers.MessageMap[str, IndexColumn]
    buildExistedData: bool
    def __init__(self, database: _Optional[str] = ..., collection: _Optional[str] = ..., indexes: _Optional[_Mapping[str, IndexColumn]] = ..., buildExistedData: bool = ...) -> None: ...

class AddIndexResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ["name", "create_time", "password", "roles", "privileges", "version"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    PRIVILEGES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    create_time: str
    password: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    privileges: _containers.RepeatedCompositeFieldContainer[Privilege]
    version: int
    def __init__(self, name: _Optional[str] = ..., create_time: _Optional[str] = ..., password: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ..., privileges: _Optional[_Iterable[_Union[Privilege, _Mapping]]] = ..., version: _Optional[int] = ...) -> None: ...

class Privilege(_message.Message):
    __slots__ = ["resource", "actions"]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    resource: str
    actions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, resource: _Optional[str] = ..., actions: _Optional[_Iterable[str]] = ...) -> None: ...

class UserAccountRequest(_message.Message):
    __slots__ = ["user", "password"]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    user: str
    password: str
    def __init__(self, user: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class UserAccountResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ...) -> None: ...

class UserPrivilegesRequest(_message.Message):
    __slots__ = ["user", "privileges"]
    USER_FIELD_NUMBER: _ClassVar[int]
    PRIVILEGES_FIELD_NUMBER: _ClassVar[int]
    user: str
    privileges: _containers.RepeatedCompositeFieldContainer[Privilege]
    def __init__(self, user: _Optional[str] = ..., privileges: _Optional[_Iterable[_Union[Privilege, _Mapping]]] = ...) -> None: ...

class UserPrivilegesResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ...) -> None: ...

class UserListRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class UserListResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "users"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    users: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., users: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class UserDescribeRequest(_message.Message):
    __slots__ = ["user"]
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class UserDescribeResponse(_message.Message):
    __slots__ = ["code", "msg", "redirect", "user"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    redirect: str
    user: User
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ..., redirect: _Optional[str] = ..., user: _Optional[_Union[User, _Mapping]] = ...) -> None: ...

class HttpRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class HttpResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
