from abc import ABC, abstractmethod
from typing import Union, List, Tuple

SparseVector = List[List[Union[int, float]]]


class BaseSparseEncoder(ABC):

    @abstractmethod
    def encode_texts(self, texts: Union[str, List[str]]) -> List[SparseVector]:
        """ 将传入的文本转换为对应的稀疏向量表示

        Args:
            texts: 原始文本，可以为str或List(str)

        Returns:
            原始文本对应的稀疏向量
        """
        pass

    @abstractmethod
    def encode_queries(self, texts: Union[str, List[str]]) -> List[SparseVector]:
        """将传入的query转换为对应的稀疏向量表示

        Args:
            texts: query文本，可以为str或List(str)

        Returns:
            文本对应的稀疏向量
        """
        pass

    @abstractmethod
    def fit_corpus(self, texts: Union[str, List[str]]):
        """根据传入的文本集，计算并调整词频、文档数等参数（即encode_texts和encode_queries步骤3中使用的参数）

        Args:
            texts: 用于训练的文本集
        """
        pass

    @abstractmethod
    def download_params(self, params_file: str):
        """下载编码参数

        Args:
            params_file：下载参数到本地文件路径
        """
        pass

    @abstractmethod
    def set_params(self, params_file: str):
        """设置编码参数

        Args:
            params_file：参数文件，根据文件中的参数替换编码过程中的参数
        """
        pass

    @abstractmethod
    def set_dict(self, dict_file: str):
        """设置自定义词表

        Args:
            dict_file：用户上传的词表文件，txt格式，单词之间用换行符或空格分隔开
        """
        pass
