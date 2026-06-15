import pytest
from src.scanner.dir_scanner import DirectoryScanner

def test_directory_scanner_initialization():
    scanner = DirectoryScanner("https://example.com")
    assert scanner.target == "https://example.com"

def test_directory_scan_executes():
    scanner = DirectoryScanner("https://example.com")
    try:
        result = scanner.scan()
        assert isinstance(result, list)
    except Exception:
        pytest.fail("DirectoryScanner.scan() failed unexpectedly")
