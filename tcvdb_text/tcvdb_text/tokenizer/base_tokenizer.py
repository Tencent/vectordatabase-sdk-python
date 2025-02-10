import os
from abc import abstractmethod
from typing import Union, List, Dict, Set, Any, Callable, Optional


class BaseTokenizer(object):
    def __init__(self,
                 hash_function: Callable[[Union[str, int]], int],
                 stop_words: Union[bool, Dict[str, Any], List[str], Set[str]] = None,
                 lower_case: bool = False,
                 dict_file: Optional[str] = None,
                 **kwargs
                 ):
        self.hash_function = hash_function
        self.stop_words = stop_words
        self.lower_case = lower_case
        self.dict_file = dict_file
        self._stop_words = None if stop_words is None else StopWords(vocab=stop_words)
        self.kwargs = kwargs

    def set_stopwords(self,
                      stop_words: Union[bool, str, Dict[str, Any], List[str], Set[str]] = True):
        self.stop_words = stop_words
        self._stop_words = None if stop_words is None else StopWords(vocab=stop_words)

    def updated_parameter(self,
                          hash_function: Callable[[Union[str, int]], int],
                          stop_words: Union[bool, str, Dict[str, Any], List[str], Set[str]] = None,
                          lower_case: bool = False,
                          dict_file: Optional[str] = None,
                          **kwargs
                          ):
        self.hash_function = hash_function
        self.stop_words = stop_words
        self.lower_case = lower_case
        self.dict_file = dict_file
        self._stop_words = None if stop_words is None else StopWords(vocab=stop_words)
        self.kwargs = kwargs

    def get_parameter(self):
        data = {
            "hash_function": self.hash_function.__name__,
            "stop_words": self.stop_words,
            "lower_case": self.lower_case,
            "dict_file": self.dict_file,
        }
        data.update(self.kwargs)
        return data

    @abstractmethod
    def tokenize(self, sentence: str) -> List[str]:
        pass

    @abstractmethod
    def encode(self, sentence: str) -> List[int]:
        pass

    @abstractmethod
    def decode(self, tokens: List[int]) -> str:
        pass

    def _is_stop_word(self, word: str) -> bool:
        if self._stop_words is None:
            return False
        return self._stop_words.check(word)

    def set_dict(self, dict_file: str):
        """Load personalized dict to improve detect rate."""
        pass


class StopWords(object):
    def __init__(self, vocab: Union[bool, Dict[str, Any], List[str], Set[str]] = None):

        self._set = set([])
        if isinstance(vocab, bool) and vocab is True:
            with open(file=os.path.dirname(os.path.realpath(__file__)) + "/../data/stopwords.txt", mode="r", encoding="utf-8") as f:
                for line in f:
                    self._set.add(line.rstrip())
        elif isinstance(vocab, str):
            if not os.path.isfile(vocab):
                vocab = os.path.dirname(os.path.realpath(__file__)) + vocab
            with open(file=vocab, mode="r") as f:
                for line in f:
                    self._set.add(line.rstrip())
        elif isinstance(vocab, (dict, list)):
            self._set = set(vocab)
        elif isinstance(vocab, set):
            self._set = vocab
        else:
            self._set = None

    def check(self, word: str) -> bool:
        if self._set is None:
            return False

        return self._set.__contains__(word)

