import os
from typing import List, Union, Dict, Any, Set, Callable, Optional

import jieba

from tcvdb_text.hash import Hash
from tcvdb_text.tokenizer import BaseTokenizer


class JiebaTokenizer(BaseTokenizer):

    def __init__(self,
                 hash_function: Callable[[Union[str, int]], int] = Hash.mmh3_hash,
                 stop_words: Union[bool, str, Dict[str, Any], List[str], Set[str]] = True,
                 lower_case: bool = False,
                 dict_file: Optional[str] = None,
                 cut_all: bool = False,
                 for_search: bool = False,
                 HMM: bool = True,
                 use_paddle: bool = False,
                 **kwargs
                 ):
        """
        Args:
            hash_function: default = mmh3 hash.
                Support for user-defined method of passing hash, the specific use of the method see example. [optional]
            stop_words (Union[bool, Dict, List, Set], optional): set stop words of tokenizer. Defaults to None.
                True/False: 'True' means using pre-defined stopwords, 'False' means not using any stopwords
                Dict/List/Set: user defined stopwords. Type [Dict]/[List] will transfer to [Set]
            lower_case: convert sentence to lowercase
            dict_file (str, optional): extra user dict path.
            cut_all:    jieba parameter
            for_search: jieba parameter
            HMM:        jieba parameter
            # use_paddle: jieba parameter

        """
        super().__init__(hash_function=hash_function,
                         stop_words=stop_words,
                         lower_case=lower_case,
                         dict_file=dict_file,
                         kwargs=kwargs)
        self.cut_all = cut_all
        self.for_search = for_search
        self.HMM = HMM
        if self.dict_file is not None:
            self.set_dict(self.dict_file)
        self.use_paddle = use_paddle
        if use_paddle:
            jieba.enable_paddle()

    def updated_parameter(self,
                          hash_function: Callable[[Union[str, int]], int] = Hash.mmh3_hash,
                          stop_words: Union[bool, Dict[str, Any], List[str], Set[str]] = False,
                          lower_case: bool = False,
                          dict_file: Optional[str] = None,
                          cut_all: bool = False,
                          for_search: bool = False,
                          HMM: bool = True,
                          use_paddle: bool = False,
                          **kwargs
                          ):
        super().updated_parameter(hash_function=hash_function,
                                  stop_words=stop_words,
                                  lower_case=lower_case,
                                  dict_file=dict_file,
                                  kwargs=kwargs)
        self.cut_all = cut_all
        self.for_search = for_search
        self.HMM = HMM
        self.use_paddle = use_paddle
        if self.dict_file is not None:
            self.set_dict(self.dict_file)
        if use_paddle:
            jieba.enable_paddle()

    def get_parameter(self):
        return {
            "hash_function": self.hash_function.__name__,
            "stop_words": self.stop_words,
            "lower_case": self.lower_case,
            "dict_file": self.dict_file,
            "cut_all": self.cut_all,
            "for_search": self.for_search,
            "HMM": self.HMM,
            "use_paddle": self.use_paddle,
        }

    def tokenize(self, sentence: str) -> List[str]:
        if not isinstance(sentence, str):
            raise TypeError(f"input sentence({sentence}) must be str")
        if len(sentence) <= 0:
            return []
        if self.lower_case:
            sentence = sentence.lower()
        words = []
        segs = []
        if self.for_search:
            segs = self.cut_for_search(sentence)
        else:
            segs = self.cut(sentence)
        for word in segs:
            if word == ' ' or word == '':
                continue
            if self._is_stop_word(word):
                continue
            words.append(word)
        return words

    def encode(self, sentence: str) -> List[int]:
        tokens = []
        for word in self.tokenize(sentence):
            tokens.append(self.hash_function(word))
        return tokens

    def decode(self, tokens: List[int]) -> str:
        raise NotImplementedError("decode method is not implemented")

    def cut(self, sentence):
        return jieba.lcut(sentence, cut_all=self.cut_all, HMM=self.HMM, use_paddle=self.use_paddle)

    def cut_for_search(self, sentence):
        return jieba.lcut_for_search(sentence, HMM=self.HMM)

    def set_dict(self, dict_file: str):
        """Load personalized dict to improve detect rate."""
        if not os.path.exists(dict_file):
            raise FileNotFoundError
        if not os.path.isfile(dict_file):
            raise ValueError("not a file")
        self.dict_file = dict_file
        jieba.load_userdict(dict_file)
