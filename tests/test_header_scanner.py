import pytest
from src.scanner.header_scanner import HeaderScanner

def test_header_scanner_initialization():
    scanner = HeaderScanner("https://example.com")
    assert scanner.target == "https://example.com"

def test_header_scan_no_crash():
    scanner = HeaderScanner("https://example.com")
    try:
        result = scanner.scan()
        assert isinstance(result, dict)
    except Exception:
        pytest.fail("HeaderScanner.scan() caused unexpected error")
