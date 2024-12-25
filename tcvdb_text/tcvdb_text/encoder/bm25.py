import json
import os
from collections import Counter
from typing import Union, List, Dict, Optional

import numpy as np
from tqdm import tqdm

from tcvdb_text.encoder import BaseSparseEncoder, SparseVector
from tcvdb_text.hash import Hash, hash_function_from_name
from tcvdb_text.tokenizer import BaseTokenizer, JiebaTokenizer


class BM25Encoder(BaseSparseEncoder):
    """
        BM25 implementation of sparse encoder.
    """

    def __init__(self, *,
                 b: float = 0.75,
                 k1: float = 1.2,
                 tokenizer: BaseTokenizer = JiebaTokenizer(hash_function=Hash.mmh3_hash),
                 ):
        """
        Args:
            b (float): default = 0.75.
                Controls the effect of document length on the calculation of the score. a larger b parameter indicates that the document length has a greater effect on the score, and vice versa.
            k1 (float): default = 1.2.
                Controls the effect of query item frequency on the computed score. a larger k1 parameter indicates a larger effect of query item frequency on the score and vice versa.
            tokenizer: default = jieba tokenizer.
                Support for user-defined incoming tokenize method.
        """
        self.b = b
        self.k1 = k1
        self.tokenizer = tokenizer
        # Learned Params
        self.token_freq: Optional[Dict[int, int]] = None
        self.doc_count: Optional[int] = None
        self.average_doc_length: Optional[float] = None
        self.total_doc_length = 0

    @staticmethod
    def default(name: str = 'zh') -> "BM25Encoder":
        """
        get a BM25Encoder with default OKAPI BM25 Model.

        Args:
            name:(str): model name.

        Return:
            BM25Encoder with default OKAPI BM25 Model.
        """

        if name == 'zh':
            path = os.path.dirname(os.path.realpath(__file__)) + "/../data/bm25_zh_default.json"
        elif name == 'en':
            path = os.path.dirname(os.path.realpath(__file__)) + "/../data/bm25_en_default.json"

        else:
            raise ValueError("input name be 'zh' or 'en'")
        encoder = BM25Encoder()
        try:
            encoder.set_params(path)
        except Exception as e:
            raise RuntimeError(f"load error: {e}")
        return encoder

    def _tf(self, text: str):
        # 分词并hash
        tokens = self.tokenizer.encode(text)
        # 统计词频
        counter = Counter(tokens)
        tokens = []
        counts = []
        for t, c in counter.items():
            tokens.append(t)
            counts.append(c)
        return tokens, counts

    def _encode_single_document(self, text: str) -> SparseVector:
        tokens, counts = self._tf(text)
        tf = np.array(counts)
        tf_sum = sum(tf)  # type: ignore
        tf_normed = (tf / (
                self.k1 * (1.0 - self.b + self.b * (tf_sum / self.average_doc_length)) + tf
        )).tolist()
        vectors: SparseVector = []
        for i in range(len(tf_normed)):
            vectors.append([tokens[i], tf_normed[i]])
        return vectors

    def encode_texts(self, texts: Union[str, List[str]]) -> Union[SparseVector, List[SparseVector]]:
        """ 将传入的文本转换为对应的稀疏向量表示
        步骤：
        1. 分词：参考jieba分词工具，支持中文、英文两种语言
        2. Hash：将步骤1中得到的word转换成唯一id，即每个word唯一对应一个id。例如["向量", "数据库"]经过hash后得到[118762, 231429]
        3. 计算每个词与文档的相关性：对每个word计算相关性，参考bm25中计算tf的方式，
                                也可参考Pinecone做法。例如["向量", "数据库"]经计算得到的相关性为[0.7612, 0.9564]
        4. 得到稀疏向量：根据步骤2、3的计算即可得到稀疏向量。例如经过步骤2、3可以得到{118762: 0.7612, 231429: 0.9564}

        Args:
            texts: 原始文本，可以为str或List(str)

        Returns:
            原始文本对应的稀疏向量
        """
        if self.token_freq is None or self.doc_count is None or self.average_doc_length is None:
            raise ValueError("BM25 must be fit before encoding documents")
        if isinstance(texts, str):
            return self._encode_single_document(texts)
        elif isinstance(texts, list):
            return [self._encode_single_document(text) for text in texts]
        else:
            raise ValueError("texts must be a string or list of strings")

    def _encode_single_query(self, text: str) -> SparseVector:
        tokens, counts = self._tf(text)
        df = np.array([self.token_freq.get(str(idx), 1) for idx in tokens])  # type: ignore
        idf = np.log((self.doc_count + 1) / (df + 0.5))   # type: ignore
        idf_norm = (idf / idf.sum()).tolist()
        vectors: SparseVector = []
        for i in range(len(idf_norm)):
            vectors.append([tokens[i], idf_norm[i]])
        return vectors

    def encode_queries(self, texts: Union[str, List[str]]) -> Union[SparseVector, List[SparseVector]]:
        """将传入的query转换为对应的稀疏向量表示
        步骤：和encode_texts类似，不同点为第3步
        1. 分词：参考jieba分词工具，支持中文、英文两种语言
        2. Hash：将步骤1中得到的word转换成唯一id，即每个word唯一对应一个id
        3. 计算每个词与文档的相关性：对每个word计算和query的相关性，参考bm25中计算「idf」的方式，也可参考Pinecone做法
        4. 得到稀疏向量

        Args:
            texts: query文本，可以为str或List(str)

        Returns:
            文本对应的稀疏向量
        """
        if self.token_freq is None or self.doc_count is None or self.average_doc_length is None:
            raise ValueError("BM25 must be fit before encoding queries")
        if isinstance(texts, str):
            return self._encode_single_query(texts)
        elif isinstance(texts, list):
            return [self._encode_single_query(text) for text in texts]
        else:
            raise ValueError("texts must be a string or list of strings")

    def fit_corpus(self, corpus: Union[str, List[str]]):
        """根据传入的文本集，计算并调整词频、文档数等参数（即encode_texts和encode_queries步骤3中使用的参数）

        Args:
            corpus: 用于训练的文本集
        """
        doc_num = 0
        sum_doc_len = 0
        token_freq_counter: Counter = Counter()

        if isinstance(corpus, str):
            corpus = [corpus]
        for doc in corpus:
            if not isinstance(doc, str):
                raise ValueError("corpus must be a list of strings")

            indices, tf = self._tf(doc)
            if len(indices) == 0:
                continue
            doc_num += 1
            sum_doc_len += sum(tf)
            # Count the number of documents that contain each token
            indices_str = [str(x) for x in indices]
            token_freq_counter.update(indices_str)
        if self.token_freq is None or self.doc_count is None or self.average_doc_length is None:
            self.token_freq = dict(token_freq_counter)
            self.doc_count = doc_num
            self.average_doc_length = sum_doc_len / doc_num
            self.total_doc_length = sum_doc_len
        else:
            if self.total_doc_length == 0:
                self.total_doc_length = self.average_doc_length * self.doc_count
            self.total_doc_length += sum_doc_len
            self.doc_count += doc_num
            self.average_doc_length = self.total_doc_length / self.doc_count
            token_freq = dict(token_freq_counter)
            for k, v in token_freq.items():
                count = self.token_freq.get(k, 0)
                self.token_freq[k] = count + v

    def download_params(self, params_file: str = "./bm25_params.json"):
        """下载BM25参数

        Args:
            params_file：下载参数到本地文件路径
        """
        if not isinstance(params_file, str):
            raise TypeError("input path must be str")
        if not params_file:
            raise ValueError("input path should not be empty")
        if self.token_freq is None or self.doc_count is None or self.average_doc_length is None:
            raise ValueError("BM25 must be fit before storing params")
        tokenizer_param = self.tokenizer.get_parameter()
        doc_sorted = sorted(self.token_freq.items())
        self.token_freq = {k: v for k, v in doc_sorted}
        data = {
            "b": self.b,
            "k1": self.k1,
            "token_freq": self.token_freq,
            "doc_count": self.doc_count,
            "average_doc_length": self.average_doc_length,
        }
        data.update(tokenizer_param)
        try:
            os.makedirs(os.path.dirname(params_file), exist_ok=True)
        except OSError as error:
            raise RuntimeError(f"create directory error: {error}")
        try:
            with open(params_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            raise RuntimeError("download params error: " + str(e))

    def set_params(self, params_file: str = "./bm25_params.json"):
        """设置BM25参数

        Args:
            params_file：参数文件，根据文件中的参数替换编码过程中的参数
        """
        if not isinstance(params_file, str):
            raise TypeError("input path must be str")
        if len(params_file) <= 0:
            raise ValueError("input path should not be empty")
        if not os.path.exists(params_file):
            raise FileNotFoundError
        if not os.path.isfile(params_file):
            raise ValueError("not a file")
        data = {}
        try:
            with open(params_file, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
        except Exception as e:
            raise RuntimeError(f"set params({params_file}) failed, error:{e}")
        self.b = data.get('b')
        self.k1 = data.get('k1')
        self.token_freq = data.get('token_freq')
        self.doc_count = data.get('doc_count')
        self.average_doc_length = data.get('average_doc_length')
        hash_function = hash_function_from_name(data.get('hash_function', 'mmh3_hash'))
        self.tokenizer.updated_parameter(hash_function=hash_function,
                                         stop_words=data.get('stop_words', True),
                                         lower_case=data.get('lower_case', False),
                                         dict_file=data.get('dict_file'),
                                         cut_all=data.get('cut_all', False),
                                         for_search=data.get('for_search', False),
                                         HMM=data.get('HMM', True),
                                         use_paddle=data.get('use_paddle', False),
                                         )
        return self

    def set_dict(self, dict_file: str):
        """Load personalized dict to improve detect rate.

        Parameter:
            - f : A plain text file contains words and their ocurrences.
                  Can be a file-like object, or the path of the dictionary file,
                  whose encoding must be utf-8.

        Structure of dict file:
        word1 freq1 word_type1
        word2 freq2 word_type2
        ...
        Word type may be ignored
        """
        self.tokenizer.set_dict(dict_file)
