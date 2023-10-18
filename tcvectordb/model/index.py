
from typing import Dict, List, Optional, Union
from tcvectordb import exceptions
from .enum import FieldType, MetricType, IndexType
from enum import Enum


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
    def __init__(self, name: str, field_type: FieldType, index_type: Enum = None):
        self._name = name
        self._field_type = field_type
        self._index_type = index_type

    @property
    def __dict__(self):
        obj = {
            'fieldName': self.name,
            'fieldType': self._field_type.value,
            'indexType': self._index_type.value
        }
        return obj

    @property
    def indexType(self):
        return self._index_type

    def is_vector_field(self) -> bool:
        return self._field_type == FieldType.Vector

    def is_primary_key(self) -> bool:
        return self._index_type == IndexType.PRIMARY_KEY

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
        name: str,
        dimension: int,
        index_type: IndexType,
        metric_type: MetricType,
        params=None,
        **kwargs
    ):
        super().__init__(name=name, field_type=FieldType.Vector)
        self._dimension = dimension
        self._index_type = index_type
        self._metric_type = metric_type
        self._param = params
        # self._indexed_count = kwargs.get('indexed_count', 0)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def dimension(self):
        return self._dimension

    @property
    def metricType(self):
        return self._metric_type

    @property
    def param(self):
        return self._param

    # @property
    # def indexed_count(self):
    #     return self._indexed_count

    @property
    def __dict__(self):
        obj = super().__dict__
        obj.update({
            'dimension': self.dimension,
            'metricType': self.metricType.value,
        })
        if self.param:
            obj['params'] = vars(self.param) if hasattr(
                self.param, '__dict__') else self.param
        if hasattr(self, 'indexedCount') and self.indexedCount:
            obj['indexedCount'] = self.indexedCount
        return obj


class FilterIndex(IndexField):
    """
    Args:
        name(str): The field name of the index.
        field_type(FieldType): The scalar field type of the index.
        index_type(IndexType): The scalar index type of the index.
    """

    def __init__(self, name: str, field_type: FieldType, index_type: IndexType, **kwargs) -> None:
        super().__init__(name=name, field_type=field_type, index_type=index_type)


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
        pass
    
    @property
    def indexes(self):
        return self._indexes

    def add(self, index: Union[FilterIndex, VectorIndex, None] = None, **kwargs):
        if not index and kwargs:
            if kwargs.get('fieldType', '') == FieldType.Vector.value:
                index = VectorIndex(
                    kwargs.pop('fieldName', ''),
                    kwargs.pop('dimension', 0),
                    IndexType(kwargs.pop('indexType', None)),
                    MetricType(kwargs.pop('metricType', None)),
                    kwargs.pop('params', None),
                    **kwargs,
                )
            else:
                index = FilterIndex(
                    kwargs.pop('fieldName', ''),
                    FieldType(kwargs.pop('fieldType', '')),
                    IndexType(kwargs.pop('indexType', None)),
                    **kwargs,
                )

        if index.name in self._indexes:
            raise exceptions.IndexTypeException(
                code=-1, message='duplicate index field with {}'.format(index))
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
