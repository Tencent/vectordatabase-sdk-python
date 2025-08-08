# Tencent VectorDB Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/tcvectordb.svg)](https://pypi.org/project/tcvectordb/)
[![Python Version](https://img.shields.io/pypi/pyversions/tcvectordb.svg)](https://pypi.org/project/tcvectordb/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Python SDK for [Tencent Cloud VectorDB](https://cloud.tencent.com/product/vdb), a fully managed vector database service that supports high-performance vector similarity search and AI-powered applications.

## ✨ Features

- **High-performance Vector Search**: Efficient similarity search for high-dimensional vectors
- **AI Integration**: Seamlessly integrate with AI models and embeddings
- **Scalable**: Built to handle large-scale vector data
- **Flexible Schema**: Support for various data types and custom schemas
- **Production Ready**: Battle-tested in production environments

## Getting started

### Prerequisites
- Python 3.7+
- Tencent Cloud account with VectorDB service enabled

### Docs
 - [Create database instance](https://cloud.tencent.com/document/product/1709/94951)
 - [API Docs](https://cloud.tencent.com/document/product/1709/96724)

### Basic Usage

```python
from tcvectordb import VectorDBClient

# Initialize client
client = VectorDBClient(
    url="your-database-url",  
    api_key="your-api-key"     
)

# Create a database
db = client.create_database("my_database")

# Create a collection with vector index
collection = db.create_collection(
    name="my_collection",
    dimension=128,  
    metric="cosine"  
)

# Insert documents with vectors
documents = [
    {"id": "1", "vector": [0.1] * 128, "text": "Sample document 1"},
    {"id": "2", "vector": [0.2] * 128, "text": "Sample document 2"}
]
collection.upsert(documents)

# Search for similar vectors
results = collection.search(
    vectors=[[0.1] * 128],  
    limit=5,                 
    output_fields=["text"] 
)

for result in results[0]:
    print(f"ID: {result.id}, Text: {result.text}, Score: {result.score}")
```

## 🔍 Examples

Explore more examples in the [examples](./examples/) directory:

- [Basic Usage](./example.py)
- [AI Database Example](./ai_db_example.py)
- [Sparse Vectors](./sparse_vector_example.py)
- [Embeddings Integration](./exampleWithEmbedding.py)
- [Full-text Search](./examples/fulltext_search.py)
- [Hybrid Search](./examples/hybrid_search_with_embedding.py)
- [And more...](./examples/)

### INSTALL

```sh
pip install tcvectordb
```
