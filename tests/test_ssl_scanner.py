import pytest
from src.scanner.ssl_scanner import SSLScanner

def test_ssl_scanner_initialization():
    scanner = SSLScanner("example.com")
    assert scanner.target == "example.com"

def test_ssl_scan_runs():
    scanner = SSLScanner("example.com")
    try:
        result = scanner.scan()
        assert isinstance(result, dict)
    except Exception:
        pytest.fail("SSLScanner.scan() raised an error")
