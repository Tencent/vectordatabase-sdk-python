from typing import Union, List, Optional, Dict
from tcvectordb.debug import Warning
from tcvectordb.client.httpclient import HTTPClient


def embedding(conn: HTTPClient,
              model: str,
              data: Union[List[str]],
              params: Optional[Dict] = None,
              data_type: Optional[str] = None,
              ) -> Dict:
    """Embedding API.

    Args:
        conn (HTTPClient): Http client.
        model (str): The model to use.
        data (Union[List[str]): The data to embedding.
        params (Dict): Model parameters, only required for certain models.
            returnDenseVector (bool): Specifies whether to return a dense vector. Defaults to true.
            returnSparseVector (bool): Specifies whether to return a sparse vector.
                                Currently, only the bge-m3 model supports sparse vectors.
        data_type (str): Embedding data type, currently, only passing `text` is supported for text-embedding


    Returns:
        Dict: Return a dict, for example:
       {
         "code": 0,
         "message": "Operation success"
         "tokenUsed": 100,
         "denseVector": [[0.12, 0.12, 0.12], [0.72, 0.72, 0.72]],
         "sparseVector": [{'test': 0.08362077, 'text1': 0.08146}, {'test': 0.08362077, 'text2': 0.08146}]
       }
    """
    body = {
        'model': model,
        'modelParams': params,
        'dataType': data_type,
        'data': data,
    }
    res = conn.post('/ai/service/embedding', body)
    warning = res.body.get('warning')
    if warning:
        Warning(warning)
    return res.body
