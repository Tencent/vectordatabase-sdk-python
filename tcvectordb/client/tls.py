from typing import Optional
import ipaddress
from urllib.parse import urlparse

class TLSConfig:
    """TLS configuration for HTTPClient and RPCClient
    
    Args:
        ca_cert_path (Optional[str]): Path to CA certificate file
        skip_verify (bool): Whether to skip TLS certificate verification (NOT recommended)
    """
    
    def __init__(self, ca_cert_path: Optional[str] = None, skip_verify: bool = False):
        self.ca_cert_path = ca_cert_path
        self.skip_verify = skip_verify
        self.service_name = "vdb.tencentcloud.com"


def _get_hostname_from_url(url: str) -> Optional[str]:
    if not url:
        return None
    parse_url = url
    if '://' not in parse_url:
        parse_url = 'http://' + parse_url
    return urlparse(parse_url).hostname

def _is_ip_hostname(url: Optional[str]) -> bool:
    hostname =  _get_hostname_from_url(url)
    if not hostname:
        return False
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False
