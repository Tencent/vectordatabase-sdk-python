from typing import Dict, List, Optional, Union
from tcvectordb import exceptions
from .enum import FieldType, MetricType, IndexType
from enum import Enum


SparseVector = List[List[Union[int, float]]]


class HNSWParams:
    """
    The hnsw vector index params.
    """

    def __init__(self, m: int, efconstruction: int) -> None:
        self.M = m
        self.efConstruction = efconstruction


class IVFFLATParams:
    def __init__(self, nlist: int):
        self._nlist = nlist

    @property
    def __dict__(self):
        return {
            'nlist': self._nlist
        }


class IVFPQParams:

    def __init__(self, nlist: int, m: int) -> None:
        self._M = m
        self._nlist = nlist

    @property
    def __dict__(self):
        return {
            'M': self._M,
            'nlist': self._nlist
        }


class IVFSQ8Params:
    def __init__(self, nlist: int):
        self._nlist = nlist

    @property
    def __dict__(self):
        return {
            'nlist': self._nlist
        }


class IVFSQ4Params(IVFSQ8Params):
    """IVF_SQ4 params"""


class IVFSQ16Params(IVFSQ8Params):
    """IVF_SQ16 params"""


class IndexField:
    def __init__(self,
                 name: str,
                 field_type: FieldType,
                 index_type: IndexType = None):
        self._name = name
        self.field_type = field_type
        self.index_type = index_type

    @property
    def __dict__(self):
        obj = {
            'fieldName': self.name,
            'fieldType': self.field_type.value,
        }
        if self.index_type is not None:
            obj['indexType'] = self.index_type.value
        return obj

    @property
    def indexType(self):
        return self.index_type

    def is_vector_field(self) -> bool:
        return self.field_type == FieldType.Vector or \
            self.field_type == FieldType.BinaryVector or \
            self.field_type == FieldType.Float16Vector or \
            self.field_type == FieldType.BFloat16Vector

    def is_sparse_vector_field(self) -> bool:
        return self.field_type == FieldType.SparseVector

    def is_primary_key(self) -> bool:
        return self.index_type == IndexType.PRIMARY_KEY

    @property
    def name(self):
        return self._name


class VectorIndex(IndexField):
    """
    Args:
        name(str): The field name of the index.
        dimension(int): The dimension of the vector.
        index_type(IndexType): The index type of the vector index.
        metric_type(MetricType): The metric type of the vector index.
        params(Any): HNSWParams if the index_type is HNSW
    """

    def __init__(
        self,
        name: str = 'vector',
        dimension: Optional[int] = None,
        index_type: Optional[IndexType] = None,
        metric_type: Optional[MetricType] = None,
        params=None,
        field_type: Optional[FieldType] = None,
        **kwargs
    ):
        self.field_type_none = False
        if field_type is None:
            field_type = FieldType.Vector
            self.field_type_none = True
        super().__init__(name=name,
                         field_type=field_type,
                         index_type=index_type)
        self._dimension = dimension
        self._index_type = index_type
        self.metric_type = metric_type
        self._param = params
        self.indexed_count = kwargs.pop('indexedCount', None)
        self.kwargs = kwargs

    @property
    def dimension(self):
        return self._dimension

    @property
    def metricType(self):
        return self.metric_type

    @property
    def param(self):
        return self._param

    @property
    def __dict__(self):
        obj = super().__dict__
        if self.dimension is not None:
            obj['dimension'] = self.dimension
        if self.param:
            obj['params'] = vars(self.param) if hasattr(
                self.param, '__dict__') else self.param
        if self.metric_type is not None:
            obj['metricType'] = self.metricType.value
        if self.indexed_count is not None:
            obj['indexedCount'] = self.indexed_count
        obj.update(self.kwargs)
        return obj


class FilterIndex(IndexField):
    """
    Args:
        name(str): The field name of the index.
        field_type(FieldType): The scalar field type of the index.
        index_type(IndexType): The scalar index type of the index.
    """

    def __init__(self,
                 name: str,
                 field_type: FieldType,
                 index_type: IndexType,
                 auto_id: Optional[str] = None,
                 **kwargs) -> None:
        super().__init__(name=name,
                         field_type=field_type,
                         index_type=index_type)
        self.auto_id = auto_id
        self.kwargs = kwargs

    @property
    def __dict__(self):
        obj = super().__dict__
        if self.auto_id is not None:
            obj['autoId'] = self.auto_id
        obj.update(self.kwargs)
        return obj


class SparseIndex(IndexField):
    """
    Args:
        name(str): The field name of the index.
        field_type(FieldType): The scalar field type of the index.
        index_type(IndexType): The scalar index type of the index.
        metric_type(MetricType): The metric type of the vector index.
    """

    def __init__(self,
                 name: str = "sparse_vector",
                 field_type: FieldType = FieldType.SparseVector,
                 index_type: IndexType = IndexType.SPARSE_INVERTED,
                 metric_type: MetricType = MetricType.IP,
                 **kwargs) -> None:
        super().__init__(name=name,
                         field_type=field_type,
                         index_type=index_type)
        self.kwargs = kwargs
        self.metric_type = metric_type

    @property
    def metricType(self):
        return self.metric_type

    @property
    def __dict__(self):
        obj = super().__dict__
        obj['metricType'] = self.metric_type.value
        obj.update(self.kwargs)
        return obj


class Index:
    def __init__(self, *args):
        """
        Args:
            FilterIndex or VectorIndex
        """
        self._indexes = {}
        if len(args) != 0:
            for index in args:
                if isinstance(index, IndexField):
                    self.add(index=index)
                else:
                    self.add(**index)
    
    @property
    def indexes(self) -> Dict[str, Union[FilterIndex, VectorIndex, SparseIndex]]:
        return self._indexes

    def add(self, index: Union[IndexField, None] = None, **kwargs):
        if not index and kwargs:
            metric_type = kwargs.pop('metricType', None)
            field_type = kwargs.pop('fieldType', '')
            if field_type in {FieldType.Vector.value, FieldType.BinaryVector.value,
                              FieldType.Float16Vector.value, FieldType.BFloat16Vector.value}:
                index = VectorIndex(
                    kwargs.pop('fieldName', ''),
                    kwargs.pop('dimension', None),
                    IndexType(kwargs.pop('indexType', None)),
                    metric_type=None if metric_type is None else MetricType(metric_type),
                    params=kwargs.pop('params', None),
                    field_type=FieldType(field_type),
                    **kwargs,
                )
            elif field_type == FieldType.SparseVector.value:
                index = SparseIndex(
                    name=kwargs.pop('fieldName', ''),
                    field_type=FieldType(field_type),
                    index_type=IndexType(kwargs.pop('indexType', None)),
                    metric_type=None if metric_type is None else MetricType(metric_type),
                    **kwargs,
                )
            else:
                index = FilterIndex(
                    kwargs.pop('fieldName', ''),
                    FieldType(field_type),
                    IndexType(kwargs.pop('indexType', None)),
                    auto_id=kwargs.pop('autoId', None),
                    **kwargs,
                )
        if index.name in self._indexes:
            raise exceptions.ServerInternalError(code=15000, message='fieldName must exist and be unique')
        if index.is_primary_key():
            self._primary_field = index
        self._indexes[index.name] = index
        return self

    def remove(self, index_name: str):
        self._indexes.pop(index_name)
        return self

    def list(self):
        l = []
        for elem in self._indexes.values():
            l.append(vars(elem))
        return l

    @property
    def __dict__(self):
        obj = {}
        for k, v in self._indexes.items():
            obj[k] = vars(v)
        return obj

    def primary_field(self):
        return self._primary_field
