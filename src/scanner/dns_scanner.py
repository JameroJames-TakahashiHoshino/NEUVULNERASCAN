import dns.resolver

class DNSScanner:
    def __init__(self, target):
        self.target = target
        self.records = {}

    def scan(self):
        dns_types = ["A", "AAAA", "MX", "NS", "TXT"]

        for record in dns_types:
            try:
                answers = dns.resolver.resolve(self.target, record)
                self.records[record] = [str(rdata) for rdata in answers]
            except Exception:
                self.records[record] = []

        return self.records
