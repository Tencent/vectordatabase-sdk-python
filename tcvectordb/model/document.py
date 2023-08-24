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
    def In(self, key: str, value: List):
        value = map(lambda x: '"'+x+'"' if type(x) is str else str(x), value)
        return '{} in ({})'.format(key, ','.join(list(value)))

    @property
    def cond(self):
        return self._cond


class HNSWSearchParams:
    """HNSWSearchParams, the params of the HNSW vector index"""
    def __init__(self, ef: int):
        self.ef = ef


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
