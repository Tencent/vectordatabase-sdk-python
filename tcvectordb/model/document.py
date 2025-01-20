from abc import ABC
from typing import Dict, List, Optional, Union

from numpy import ndarray

from tcvectordb.model.index import SparseVector


class Filter:
    """
    Filter, used for the searching document, can filter the scalar indexes.
    """

    def __init__(self, cond: str):
        self._cond = cond

    def And(self, cond: str):
        self._cond = '({}) and ({})'.format(self.cond, cond)
        return self

    def Or(self, cond: str):
        self._cond = '({}) or ({})'.format(self.cond, cond)
        return self

    def AndNot(self, cond: str):
        self._cond = '({}) and not ({})'.format(self.cond, cond)
        return self

    def OrNot(self, cond: str):
        self._cond = '({}) or not ({})'.format(self.cond, cond)
        return self

    @classmethod
    def Include(self, key: str, value: List):
        value = map(lambda x: '"' + x + '"' if type(x) is str else str(x), value)
        return '{} include ({})'.format(key, ','.join(list(value)))

    @classmethod
    def Exclude(self, key: str, value: List):
        value = map(lambda x: '"' + x + '"' if type(x) is str else str(x), value)
        return '{} exclude ({})'.format(key, ','.join(list(value)))

    @classmethod
    def IncludeAll(self, key: str, value: List):
        value = map(lambda x: '"' + x + '"' if type(x) is str else str(x), value)
        return '{} include all ({})'.format(key, ','.join(list(value)))

    @classmethod
    def In(self, key: str, value: List):
        value = map(lambda x: '"' + x + '"' if type(x) is str else str(x), value)
        return '{} in ({})'.format(key, ','.join(list(value)))

    @classmethod
    def NotIn(self, key: str, value: List):
        value = map(lambda x: '"' + x + '"' if type(x) is str else str(x), value)
        return '{} not in ({})'.format(key, ','.join(list(value)))

    @property
    def cond(self):
        return self._cond

    @property
    def __dict__(self):
        return self.cond


class HNSWSearchParams:
    """HNSWSearchParams, the params of the HNSW vector index"""

    def __init__(self, ef: int):
        self.ef = ef


class SearchParams(HNSWSearchParams):
    def __init__(self, ef: int = 0, nprobe: int = 0, radius: float = 0):
        if ef > 0:
            self._ef = ef

        if nprobe > 0:
            self._nprobe = nprobe

        if radius > 0:
            self._radius = radius

    @property
    def __dict__(self):
        res = {}
        if hasattr(self, "_ef"):
            res["ef"] = self._ef
        if hasattr(self, "_nprobe"):
            res["nprobe"] = self._nprobe
        if hasattr(self, "_radius"):
            res["radius"] = self._radius
        return res


class AnnSearch:
    """ann search params"""

    def __init__(self,
                 field_name: Optional[str] = "vector",
                 document_ids: Optional[List[str]] = None,
                 data: Optional[Union[List[float], ndarray, str]] = None,
                 params: Optional[Union[HNSWSearchParams, SearchParams, dict]] = None,
                 limit: Optional[int] = None,
                 **kwargs
                 ):
        self.field_name = field_name
        self.document_ids = document_ids
        self.data = data.tolist() if isinstance(data, ndarray) else data
        self.params = params
        self.limit = limit
        self.kwargs = kwargs

    @property
    def __dict__(self):
        res = {}
        if self.field_name is not None:
            res['fieldName'] = self.field_name
        if self.document_ids is not None:
            res['documentIds'] = self.document_ids
        if self.data is not None:
            # hybrid_search sdk暂时不提供batch，但接口是batch
            if isinstance(self.data, str):
                res['data'] = [self.data]
            elif len(self.data) > 0 and (isinstance(self.data[0], str) or isinstance(self.data[0], list)):
                res['data'] = self.data
            else:
                res['data'] = [self.data]
        if self.params:
            if isinstance(self.params, dict):
                res['params'] = self.params
            else:
                res['params'] = vars(self.params)
        if self.limit is not None:
            res['limit'] = self.limit
        res.update(self.kwargs)
        return res


class KeywordSearch:
    """sparse vector search params"""

    def __init__(self,
                 field_name: Optional[str] = "sparse_vector",
                 data: Optional[SparseVector] = None,
                 limit: Optional[int] = None,
                 terminate_after: Optional[int] = None,
                 cutoff_frequency: Optional[float] = None,
                 **kwargs
                 ):
        self.field_name = field_name
        self.data = data
        self.limit = limit
        self.terminate_after = terminate_after
        self.cutoff_frequency = cutoff_frequency
        self.kwargs = kwargs

    @property
    def __dict__(self):
        res = {}
        if self.field_name is not None:
            res['fieldName'] = self.field_name
        if self.data is not None:
            if isinstance(self.data, list):
                if len(self.data) == 0:
                    res['data'] = [self.data]
                elif isinstance(self.data[0], list) \
                        and len(self.data[0]) > 0 and type(self.data[0][0]) == int:
                    res['data'] = [self.data]
                else:
                    res['data'] = self.data
        if self.limit is not None:
            res['limit'] = self.limit
        if self.terminate_after is not None:
            res['terminateAfter'] = self.terminate_after
        if self.cutoff_frequency is not None:
            res['cutoffFrequency'] = self.cutoff_frequency
        res.update(self.kwargs)
        return res


class Rerank(ABC):
    def __init__(self,
                 method: Optional[str] = None,
                 ):
        self.method = method


class WeightedRerank(Rerank):
    def __init__(self,
                 field_list: Optional[List[str]] = None,
                 weight: Optional[List[float]] = None,
                 **kwargs
                 ):
        super().__init__(method="weighted")
        self.field_list = field_list
        self.weight = weight
        self.kwargs = kwargs

    @staticmethod
    def weight_normalization(weights: List[float]) -> List[float]:
        total = sum(weights)
        if total == 0:
            return weights
        all_zero = True
        n_weights = []
        for w in weights:
            if w < 0:
                return weights
            if w != 0:
                all_zero = False
            n_weights.append(w / total)
        return weights if all_zero else n_weights

    @property
    def __dict__(self):
        res = {}
        if self.method is not None:
            res['method'] = self.method
        if self.field_list is not None:
            res['fieldList'] = self.field_list
        if self.weight is not None:
            res['weight'] = self.weight
        res.update(self.kwargs)
        return res


class RRFRerank(Rerank):
    def __init__(self,
                 k: Optional[int] = None,
                 **kwargs
                 ):
        super().__init__(method="rrf")
        self.k = k
        self.kwargs = kwargs

    @property
    def __dict__(self):
        res = {}
        if self.method is not None:
            res['method'] = self.method
        if self.k is not None:
            res['k'] = self.k
        res.update(self.kwargs)
        return res


class Document:
    """
    Document, the object for document upsert, query and search, the parameter depends on
    the structure of the index in the collection.
    """

    def __init__(self, **kwargs) -> None:
        if 'score' in kwargs:
            self._score = kwargs.pop('score')
        if 'vector' in kwargs:
            if isinstance(kwargs.get('vector', None), ndarray):
                kwargs['vector'] = kwargs.get('vector').tolist()
        self._data = kwargs

    @property
    def __dict__(self):
        return self._data
