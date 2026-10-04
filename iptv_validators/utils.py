import ipaddress
import socket
from urllib.parse import urlparse, urlunparse


def is_ssrf_safe(url: str) -> bool:
    """
    Check if a URL is safe from SSRF.
    Checks for loopback, private IP ranges, and metadata endpoints.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to IP address
        ip_addrs = socket.getaddrinfo(hostname, None)
        for addr in ip_addrs:
            ip_str = addr[4][0]
            ip = ipaddress.ip_address(ip_str)

            if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast:
                return False

            # Specific check for common cloud metadata endpoints (e.g., 169.254.169.254)
            if ip_str == "169.254.169.254":
                return False

        return True
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize a URL for deduplication purposes.
    Lowercases scheme and host, and removes unnecessary parts.
    """
    try:
        parsed = urlparse(url.strip())
        if not parsed.scheme or not parsed.netloc:
            return url.strip()

        # Lowercase scheme and netloc
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # Reconstruct the URL without fragments or queries if necessary,
        # but for IPTV, queries might be important (e.g., auth tokens).
        # So we keep query and path.
        path = parsed.path
        query = parsed.query
        fragment = "" # Strip fragment

        return urlunparse((scheme, netloc, path, '', query, fragment))
    except Exception:
        return url.strip()
