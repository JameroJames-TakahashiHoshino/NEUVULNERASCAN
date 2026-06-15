import pytest
from src.scanner.sqli_scanner import SQLiScanner

def test_sqli_scanner_initialization():
    scanner = SQLiScanner("https://example.com/login")
    assert scanner.target == "https://example.com/login"

def test_sqli_scan_executes():
    scanner = SQLiScanner("https://example.com/login")
    try:
        result = scanner.scan()
        assert isinstance(result, dict)
    except Exception:
        pytest.fail("SQLiScanner.scan() crashed")
