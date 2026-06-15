import requests

class SQLiScanner:
    def __init__(self, target):
        self.target = target
        self.payloads = ["'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1"]

    def scan(self):
        vulnerabilities = []

        for payload in self.payloads:
            try:
                r = requests.get(self.target + payload)
                if "error" in r.text.lower() or "syntax" in r.text.lower():
                    vulnerabilities.append(payload)
            except Exception:
                pass

        return vulnerabilities
