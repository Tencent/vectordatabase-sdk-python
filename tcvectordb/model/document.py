from typing import Dict, List, Optional, Union


class Filter:
    """
    Filter, used for the searching document, can filter the scalar indexes.
    """

    def __init__(self, cond: str):
        self._cond = cond

    def And(self, cond: str):
        self._cond = '{} and {}'.format(self.cond, cond)
        return self

    def Or(self, cond: str):
        self._cond = '{} or {}'.format(self.cond, cond)
        return self

    def AndNot(self, cond: str):
        self._cond = '{} and not {}'.format(self.cond, cond)
        return self

    def OrNot(self, cond: str):
        self._cond = '{} or not {}'.format(self.cond, cond)
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


class Document:
    """
    Document, the object for document upsert, query and search, the parameter depends on
    the structure of the index in the collection.
    """

    def __init__(self, **kwargs) -> None:
        if 'score' in kwargs:
            self._score = kwargs.pop('score')
        self._data = kwargs

    @property
    def __dict__(self):
        return self._data
