import platform
import requests
import socket
from urllib3.connection import HTTPConnection
from requests.adapters import HTTPAdapter
from requests.adapters import PoolManager
from urllib import parse
import json

from tcvectordb.exceptions import ParamError
from tcvectordb.exceptions import ServerInternalError
from tcvectordb import exceptions
from tcvectordb.debug import Debug


class Response():
    def __init__(self, path, res: requests.Response):
        """
        Response parse the requests package Response to code, message and data
        Args:
            path(str): The request path, used for debug print
            res(requests.Response): The requests response.
        """
        if not res.ok:
            if ('code' not in res.text) or ('msg' not in res.text):
                raise exceptions.ServerInternalError(code=res.status_code,
                                                     message='{}: {}'.format(res.reason, res.text))
        try:
            response = res.json()
            self._code = int(response.get('code', 0))
            self._message = response.get('msg', '')
            self._body = response
            # print debug message if set DebugEnable is True
            Debug("RESPONSE: %s", path)
            Debug(json.dumps(response, indent=2))
        except Exception as e:
            raise exceptions.ServerInternalError(
                code=-1, message=str(res.content)+' ' + str(e))

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def body(self) -> dict:
        return self._body

    def data(self) -> dict:
        res = {}
        res.update(self._body)
        return res


class HTTPClient:
    def __init__(self, url: str, username: str, key: str,
                 timeout: int = None, adapter: HTTPAdapter = None):
        """
        Create a httpclient session.
        Args:
            url(str): the url of vectordb, support http only
            username(str): the vectordb username, support root only currently
            key(str): account api key from console
            timeout(int): default http timeout by second, if set 0, means no timeout
        """
        parse_result = parse.urlparse(url)
        self.scheme = parse_result.scheme
        if self.scheme == 'https':
            raise ParamError
        self.url = url
        self.username = username
        self.key = key
        self.timeout = timeout
        self.header = {
            'Authorization': 'Bearer {}'.format(self._authorization()),
        }
        self.session = requests.Session()
        self._set_adapter(adapter)

    def _set_adapter(self, adapter: HTTPAdapter = None):
        if not adapter:
            if 'linux' not in platform.platform().lower():
                return
            options = HTTPConnection.default_socket_options + [
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120),
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3),
            ]
            adapter = _SockOpsAdapter(pool_connections=10,
                                      pool_maxsize=10, max_retries=3, options=options)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _authorization(self):
        if not self.username or not self.key:
            raise ParamError

        return 'account={0}&api_key={1}'.format(self.username, self.key)

    def _get_url(self, path):
        if not self.url:
            raise ParamError
        return self.url + path

    """ wrap the requests get method
    Raise: ServerInternalError when response code is not 0
    """

    def get(self, path, params=None, timeout=None) -> Response:
        if not timeout:
            timeout = self.timeout
        if timeout is not None and timeout <= 0:
            timeout = None
        Debug("GET %s", path)
        Debug('params: %s', json.dumps(params, indent=2))
        res = self.session.get(self._get_url(
            path), params=params, headers=self.header, timeout=timeout)

        response = Response(path, res)
        if response.code != 0:
            raise ServerInternalError(
                code=response.code, message=response.message)
        return response

    """ wrap the requests post method
    Raise: ServerInternalError when response code is not 0
    """

    def post(self, path, body, timeout=None) -> Response:
        if not timeout:
            timeout = self.timeout
        if timeout is not None and timeout <= 0:
            timeout = None
        Debug('POST %s', path)
        Debug('body: %s', json.dumps(body, indent=2))
        res = self.session.post(self._get_url(
            path), json=body, headers=self.header, timeout=timeout)

        response = Response(path, res)
        if response.code != 0:
            raise ServerInternalError(
                code=response.code, message=response.message)
        return response

    def close(self):
        self.session.close()


class _SockOpsAdapter(HTTPAdapter):
    def __init__(self, options, **kwargs):
        self.options = options
        super(_SockOpsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       socket_options=self.options)
