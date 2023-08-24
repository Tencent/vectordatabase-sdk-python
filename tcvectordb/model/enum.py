from enum import Enum, unique


@unique
class FieldType(Enum):
    """
    Field type of index field
    """
    # scalar field type
    Uint64 = "uint64"
    String = "string"

    # vector field type
    Vector = "vector"


@unique
class MetricType(Enum):
    """
    The metric type of the vector index.
    """
    L2 = "L2"
    IP = "IP"
    COSINE = "COSINE"


@unique
class IndexType(Enum):
    # vector index type
    FLAT = "FLAT"
    HNSW = "HNSW"

    # scalar index type
    PRIMARY_KEY = "primaryKey"
    FILTER = "filter"
