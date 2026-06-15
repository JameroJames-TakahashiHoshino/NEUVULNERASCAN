import ssl
import socket
from urllib.parse import urlparse


class SSLScanner:
    def __init__(self, target: str):
        # Keep original target string for reporting/tests
        self.target = target
        self.host = self._normalize_host(target)

    def _normalize_host(self, value: str) -> str:
        """Extract a bare hostname from a URL or host string.

        Examples:
          - "https://www.youtube.com/watch?v=123" -> "www.youtube.com"
          - "example.com/path" -> "example.com"
          - "example.com:8443" -> "example.com"
        """
        v = (value or "").strip()
        if not v:
            return ""

        host = v
        if "://" in v:
            parsed = urlparse(v)
            host = parsed.hostname or ""
        else:
            # Strip any path/query if user pasted something like "example.com/some/path"
            host = v.split("/", 1)[0]

        # If a port is present (host:port), keep only the hostname
        host = host.split(":", 1)[0]
        return host

    def scan(self):
        ctx = ssl.create_default_context()

        try:
            with socket.create_connection((self.host, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert() or {}
                    return cert
        except socket.gaierror as e:
            # DNS resolution failed (e.g., invalid host or offline)
            return {"error": f"DNS resolution failed for {self.host}: {e}"}
        except (socket.timeout, OSError, ssl.SSLError) as e:
            # Network/SSL issues should not crash the whole scan
            return {"error": f"SSL connection failed for {self.host}: {e}"}
