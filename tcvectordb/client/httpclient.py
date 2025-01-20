import platform
from typing import Optional

import requests
import socket
from urllib3.connection import HTTPConnection
from requests.adapters import HTTPAdapter
from requests.adapters import PoolManager

from tcvectordb.exceptions import ParamError
from tcvectordb.exceptions import ServerInternalError
from tcvectordb import exceptions, debug


class Response():
    def __init__(self, path, res: requests.Response):
        """Http Response

        Args:
            path(str): The request path, used for debug print
            res(requests.Response): The requests response.
        """
        if not res.ok:
            if ('code' not in res.text) or ('msg' not in res.text):
                message = res.text
                if res.status_code >= 500:
                    message = f'{message}\n{exceptions.ERROR_MESSAGE_NETWORK_OR_AUTH}'
                raise exceptions.ServerInternalError(code=res.status_code,
                                                     message='{}: {}'.format(res.reason, message))
        try:
            response = res.json()
            self._code = int(response.get('code', 0))
            self._message = response.get('msg', '')
            self._body = response
            # print debug message if set DebugEnable is True
            debug.Debug("Response %s, content=%s", path, response)
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
                 timeout: int = 10,
                 adapter: HTTPAdapter = None,
                 pool_size: int = 10,
                 proxies: Optional[dict] = None,
                 password: Optional[str] = None):
        """
        Create a httpclient session.
        Args:
            url(str): the url of vectordb, support http only
            username(str): the vectordb username, support root only currently
            key(str): account api key from console
            timeout(int): default http timeout by second, if set 0, means no timeout
        """
        self.url = url
        self.username = username
        self.key = key
        self.password = password
        self.timeout = timeout
        self.header = {
            'Authorization': 'Bearer {}'.format(self._authorization()),
        }
        self.pool_size = pool_size
        self.session = requests.Session()
        if proxies:
            self.session.proxies = proxies
        self._set_adapter(adapter)
        self.direct = False

    def _get_headers(self, ai: Optional[bool] = False):
        if ai is None:
            return self.header
        backend = "vdb"
        if not self.direct and ai:
            backend = "ai"
        header = {
            'backend-service': backend
        }
        header.update(self.header)
        # debug.Debug("Backend %s", backend)
        return header

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
            adapter = _SockOpsAdapter(pool_connections=self.pool_size,
                                      pool_maxsize=self.pool_size,
                                      max_retries=3,
                                      options=options)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _authorization(self):
        if self.password is None:
            self.password = self.key
        if not self.username or not self.password:
            raise ParamError(message=exceptions.ERROR_MESSAGE_NETWORK_OR_AUTH)
        return 'account={0}&api_key={1}'.format(self.username, self.password)

    def _get_url(self, path):
        if not self.url:
            raise ParamError(message=exceptions.ERROR_MESSAGE_NETWORK_OR_AUTH)
        return self.url + path

    def _warning(self, headers):
        if not headers:
            return
        warn = headers.get('Warning')
        if warn:
            Warning(warn)

    def get(self, path, params=None, timeout=None, ai: Optional[bool] = False) -> Response:
        if not timeout:
            timeout = self.timeout
        if timeout is not None and timeout <= 0:
            timeout = None
        debug.Debug("GET %s, params=%s", path, params)
        try:
            res = self.session.get(self._get_url(
                path), params=params, headers=self._get_headers(ai), timeout=timeout)
        except requests.exceptions.ConnectionError as e:
            raise exceptions.ConnectError(
                message='{}: {}'.format(str(e), exceptions.ERROR_MESSAGE_NETWORK_OR_AUTH))
        self._warning(res.headers)
        response = Response(path, res)
        if response.code != 0:
            raise ServerInternalError(
                code=response.code, message=response.message)
        return response

    """ wrap the requests post method
    Raise: ServerInternalError when response code is not 0
    """

    def post(self, path, body, timeout=None, ai: Optional[bool] = False) -> Response:
        if not timeout:
            timeout = self.timeout
        if timeout is not None and timeout <= 0:
            timeout = None
        debug.Debug('POST %s, body=%s', path, body)
        try:
            res = self.session.post(self._get_url(
                path), json=body, headers=self._get_headers(ai), timeout=timeout)
        except requests.exceptions.ConnectionError as e:
            raise exceptions.ConnectError(
                message='{}: {}'.format(str(e), exceptions.ERROR_MESSAGE_NETWORK_OR_AUTH))
        self._warning(res.headers)
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
