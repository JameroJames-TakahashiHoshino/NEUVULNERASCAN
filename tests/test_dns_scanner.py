import pytest
from src.scanner.dns_scanner import DNSScanner

def test_dns_scanner_initialization():
    scanner = DNSScanner("google.com")
    assert scanner.target == "google.com"

def test_dns_scan_runs_without_crashing():
    scanner = DNSScanner("google.com")
    try:
        result = scanner.scan()
        assert isinstance(result, dict)
    except Exception:
        pytest.fail("DNSScanner.scan() crashed unexpectedly")
