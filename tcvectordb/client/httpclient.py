import platform
from typing import Optional
from pathlib import Path

import requests
import socket
import urllib3
from urllib3.connection import HTTPConnection
from requests.adapters import HTTPAdapter
from requests.adapters import PoolManager

from tcvectordb.exceptions import ParamError
from tcvectordb.exceptions import ServerInternalError
from tcvectordb import exceptions, debug
from tcvectordb.client.tls import TLSConfig
from tcvectordb.client.tls import _is_ip_hostname

urllib3.disable_warnings()

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
            self.req_id = response.get('requestId', None)
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
                 password: Optional[str] = None,
                 tls_config: Optional[TLSConfig] = None):
        """
        Create a httpclient session.
        Args:
            url(str): the url of vectordb, support http only
            username(str): the vectordb username, support root only currently
            key(str): account api key from console
            timeout(int): default http timeout by second, if set 0, means no timeout
            tls_config(Optional[TLSConfig]): TLS configuration for secure connections
        """
        self.url = url
        self.username = username
        self.key = key
        self.password = password
        self.timeout = timeout
        self.tls_config = tls_config
        self.header = {
            'Authorization': 'Bearer {}'.format(self._authorization()),
        }
        self.pool_size = pool_size
        self.session = requests.Session()
        self._configure_tls()

        if proxies:
            self.session.proxies = proxies
        self._set_adapter(adapter)
        self.direct = False

    def _configure_tls(self):
        # Set verify parameter for TLS configuration
        if not self.tls_config or self.tls_config.skip_verify:
            self.session.verify = False
        elif self.tls_config and self.tls_config.ca_cert_path:
            ca_cert = Path(self.tls_config.ca_cert_path)
            if not ca_cert.exists():
                raise FileNotFoundError(f"ca cert file not exist: {self.tls_config.ca_cert_path}")
            self.session.verify = self.tls_config.ca_cert_path
            if _is_ip_hostname(self.url):
                self.header['Host'] = self.tls_config.service_name

    def _get_url(self, path):
        if not self.url:
            raise ParamError(message=exceptions.ERROR_MESSAGE_NETWORK_OR_AUTH)
        return self.url + path

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
        self.session.mount('https://', HostHeaderSSLAdapter(adapter.options))

    def _authorization(self):
        if self.password is None:
            self.password = self.key
        if not self.username or not self.password:
            raise ParamError(message=exceptions.ERROR_MESSAGE_NETWORK_OR_AUTH)
        return 'account={0}&api_key={1}'.format(self.username, self.password)

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
                code=response.code, message=response.message, req_id=response.req_id)
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
                code=response.code, message=response.message, req_id=response.req_id)
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

class HostHeaderSSLAdapter(_SockOpsAdapter, HTTPAdapter):
    """
    A HTTPS Adapter for Python Requests that sets the hostname for certificate
    verification based on the Host header.

    This allows requesting the IP address directly via HTTPS without getting
    a "hostname doesn't match" exception.

    Example usage:

        >>> s.mount('https://', HostHeaderSSLAdapter())
        >>> s.get("https://93.184.216.34", headers={"Host": "example.org"})

    """

    def __init__(self, *args, **kwargs):
        super(HostHeaderSSLAdapter, self).__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        # HTTP headers are case-insensitive (RFC 7230)
        host_header = None
        for header in request.headers:
            if header.lower() == "host":
                host_header = request.headers[header]
                break

        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        if host_header:
            connection_pool_kwargs["assert_hostname"] = host_header
        elif "assert_hostname" in connection_pool_kwargs:
            # an assert_hostname from a previous request may have been left
            connection_pool_kwargs.pop("assert_hostname", None)

        return super(HostHeaderSSLAdapter, self).send(request, **kwargs)