import os
import tcvdb_text
from tcvdb_text.encoder import BM25Encoder
from tcvdb_text.tokenizer import JiebaTokenizer


def quick_start():
    bm25 = BM25Encoder.default('zh')
    text_vector = bm25.encode_texts(
        '腾讯云向量数据库（Tencent Cloud VectorDB）是一款全托管的自研企业级分布式数据库服务，专用于存储、索引、检索、管理由深度神经网络或其他机器学习模型生成的大量多维嵌入向量。'
    )

    print('encode single text: {}'.format(text_vector))
    text_vectors = bm25.encode_texts([
        '作为专门为处理输入向量查询而设计的数据库，它支持多种索引类型和相似度计算方法，单索引支持10亿级向量规模，高达百万级 QPS 及毫秒级查询延迟。',
        '不仅能为大模型提供外部知识库，提高大模型回答的准确性，还可广泛应用于推荐系统、NLP 服务、计算机视觉、智能客服等 AI 领域。'
    ])
    print('encode multiple texts: {}'.format(text_vectors))
    query_vector = bm25.encode_queries('什么是腾讯云向量数据库？')
    print('encode single query: {}'.format(query_vector))
    query_vectors = bm25.encode_queries(['腾讯云向量数据库有什么优势？', '腾讯云向量数据库能做些什么？'])
    print('encode multiple quires: {}'.format(query_vectors))


def fit_and_load():
    bm25 = BM25Encoder.default('zh')
    bm25.set_dict(os.path.dirname(tcvdb_text.__file__) + '/data/userdict_example.txt')
    print('fit with your own corpus')
    bm25.fit_corpus([
        '腾讯云向量数据库（Tencent Cloud VectorDB）是一款全托管的自研企业级分布式数据库服务，专用于存储、索引、检索、管理由深度神经网络或其他机器学习模型生成的大量多维嵌入向量。',
        '作为专门为处理输入向量查询而设计的数据库，它支持多种索引类型和相似度计算方法，单索引支持10亿级向量规模，高达百万级 QPS 及毫秒级查询延迟。',
        '不仅能为大模型提供外部知识库，提高大模型回答的准确性，还可广泛应用于推荐系统、NLP 服务、计算机视觉、智能客服等 AI 领域。',
        '腾讯云向量数据库（Tencent Cloud VectorDB）作为一种专门存储和检索向量数据的服务提供给用户， 在高性能、高可用、大规模、低成本、简单易用、稳定可靠等方面体现出显著优势。 ',
        '腾讯云向量数据库可以和大语言模型 LLM 配合使用。企业的私域数据在经过文本分割、向量化后，可以存储在腾讯云向量数据库中，构建起企业专属的外部知识库，从而在后续的检索任务中，为大模型提供提示信息，辅助大模型生成更加准确的答案。',
        '腾讯云数据库托管机房分布在全球多个位置，这些位置节点称为地域（Region），每个地域又由多个可用区（Zone）构成。每个地域（Region）都是一个独立的地理区域。每个地域内都有多个相互隔离的位置，称为可用区（Zone）。每个可用区都是独立的，但同一地域下的可用区通过低时延的内网链路相连。腾讯云支持用户在不同位置分配云资源，建议用户在设计系统时考虑将资源放置在不同可用区以屏蔽单点故障导致的服务不可用状态。'
    ])
    print('download bm25 params')
    bm25.download_params()
    print('load bm25 params')
    bm25.set_params()
    query_vectors = bm25.encode_queries(['什么是腾讯云向量数据库？', '腾讯云向量数据库有什么优势？', '腾讯云向量数据库能做些什么？'])
    print('encode with your own fit params: {}'.format(query_vectors))


if __name__ == '__main__':
    quick_start()
    fit_and_load()
