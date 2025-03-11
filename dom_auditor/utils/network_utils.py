import requests
import urllib.parse
import socket
import logging
from typing import Dict, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)

def fetch_url(url: str, timeout: int = 10, headers: Dict[str, str] = None) -> Tuple[Optional[str], int, Dict[str, str]]:
    """Fetch content from a URL with timeout and optional headers."""
    try:
        if not headers:
            headers = {
                'User-Agent': 'DOM-Auditor/0.1.0'
            }
        
        response = requests.get(url, timeout=timeout, headers=headers)
        return response.text, response.status_code, dict(response.headers)
    
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None, 0, {}

def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_domain_info(domain: str) -> Dict[str, Any]:
    """Get information about a domain."""
    try:
        ip_address = socket.gethostbyname(domain)
        return {
            'domain': domain,
            'ip_address': ip_address,
            'resolved': True
        }
    except socket.gaierror:
        return {
            'domain': domain,
            'resolved': False
        }

def download_file(url: str, local_path: str) -> bool:
    """Download a file from a URL to a local path."""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Error downloading file from {url} to {local_path}: {e}")
        return False

def check_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open on a host."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except Exception:
        return False
    finally:
        s.close()