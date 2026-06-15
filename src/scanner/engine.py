from .port_scanner import PortScanner
from .dns_scanner import DNSScanner
from .header_scanner import HeaderScanner
from .sqli_scanner import SQLiScanner
from .dir_scanner import DirectoryScanner
from .ssl_scanner import SSLScanner
from urllib.parse import urlparse

class NeuVulneraScanEngine:
    def __init__(self, target):
        # Preserve the original input exactly as provided
        self.target = target
        self.results = {}

        # Derived forms of the target used by different scanners
        self._host_target = self._normalize_host(target)
        self._url_target = self._normalize_url(target)

    def _normalize_host(self, value: str) -> str:
        """Return a bare hostname/IP for scanners that expect a host only.

        Examples:
          - "https://example.com/path" -> "example.com"
          - "example.com/some/path" -> "example.com"
          - "27.49.10.65" -> "27.49.10.65"
        """
        v = (value or "").strip()
        if not v:
            return ""

        host = v
        if "://" in v:
            parsed = urlparse(v)
            host = parsed.hostname or ""
        else:
            # Strip any path if present
            host = v.split("/", 1)[0]

        # If a port is present (host:port), keep only the hostname/IP
        host = host.split(":", 1)[0]
        return host

    def _normalize_url(self, value: str) -> str:
        """Return a URL suitable for HTTP requests.

        If no scheme is supplied (e.g. "example.com" or "27.49.10.65"),
        default to http:// so that requests.get() receives a valid URL.
        """
        v = (value or "").strip()
        if not v:
            return ""

        # If it already looks like a full URL, use as-is
        if v.startswith("http://") or v.startswith("https://"):
            return v
        if "://" in v:
            return v

        # Fallback: treat it as a bare host/IP and prepend http://
        return f"http://{v}"

    def run_all(self):
        # Scanners that operate on a host/IP only
        host = self._host_target or self.target
        self.results["ports"] = PortScanner(host).scan()
        self.results["dns"] = DNSScanner(host).scan()

        # Scanners that expect a full URL (including scheme)
        url = self._url_target
        self.results["headers"] = HeaderScanner(url).scan()
        self.results["sqli"] = SQLiScanner(url).scan()
        self.results["directories"] = DirectoryScanner(url).scan()

        # SSL scanner can work from the host/hostname
        self.results["ssl"] = SSLScanner(host).scan()

        return self.results
