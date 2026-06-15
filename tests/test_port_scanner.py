import pytest
from src.scanner.port_scanner import PortScanner

def test_port_scanner_initialization():
    scanner = PortScanner("127.0.0.1")
    assert scanner.target == "127.0.0.1"

def test_port_scanner_scan_runs():
    scanner = PortScanner("127.0.0.1")
    try:
        result = scanner.scan()
        assert isinstance(result, dict)
    except Exception:
        pytest.fail("PortScanner.scan() raised an exception")
