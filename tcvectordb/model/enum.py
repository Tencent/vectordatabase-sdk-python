from enum import Enum, unique


@unique
class FieldType(Enum):
    """
    Field type of index field
    """
    # scalar field type
    Uint64 = "uint64"
    String = "string"
    Array = "array"

    # vector field type
    Vector = "vector"
    # sparse vector type
    SparseVector = "sparseVector"


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
    IVF_FLAT = "IVF_FLAT"
    IVF_PQ = "IVF_PQ"
    IVF_SQ4 = "IVF_SQ4"
    IVF_SQ8 = "IVF_SQ8"
    IVF_SQ16 = "IVF_SQ16"

    # scalar index type
    PRIMARY_KEY = "primaryKey"
    FILTER = "filter"
    SPARSE_INVERTED = "inverted"


@unique
class EmbeddingModel(Enum):
    BGE_BASE_ZH = ("bge-base-zh", 768)
    M3E_BASE = ("m3e-base", 768)
    TEXT2VEC_LARGE_CHINESE = ("text2vec-large-chinese", 1024)
    E5_LARGE_V2 = ("e5-large-v2", 1024)
    MULTILINGUAL_E5_BASE = ("multilingual-e5-base", 768)

    def __init__(self, name: str, dimensions: int):
        self.__name = name
        self.__dimensions = dimensions

    @property
    def model_name(self):
        return self.__name


@unique
class ReadConsistency(Enum):
    STRONG_CONSISTENCY = "strongConsistency"
    EVENTUAL_CONSISTENCY = "eventualConsistency"

    def __init__(self, value: str):
        self.__value = value

    @property
    def value(self):
        return self.__value
