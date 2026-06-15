import requests


class HeaderScanner:
    def __init__(self, target):
        self.target = target
        self.results = {}

    def scan(self):
        try:
            # Use a sensible timeout so unreachable hosts don't hang forever
            r = requests.get(self.target, timeout=5)
            headers = dict(r.headers)
        except requests.exceptions.RequestException as e:
            # Network-related issue (timeout, DNS failure, connection error, etc.)
            self.results["error"] = f"Failed to fetch headers from {self.target}: {e}"
            self.results["headers"] = {}
            self.results["missing_headers"] = []
            return self.results

        required_headers = [
            "Content-Security-Policy",
            "X-Frame-Options",
            "Strict-Transport-Security",
            "X-Content-Type-Options"
        ]

        missing = [h for h in required_headers if h not in headers]
        self.results["headers"] = headers
        self.results["missing_headers"] = missing

        return self.results
