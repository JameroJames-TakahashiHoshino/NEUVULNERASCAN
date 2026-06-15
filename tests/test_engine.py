import pytest
from src.scanner.engine import NeuVulneraScanEngine

def test_engine_initialization():
    engine = NeuVulneraScanEngine("https://example.com")
    assert engine.target == "https://example.com"

def test_engine_run_all():
    engine = NeuVulneraScanEngine("https://example.com")
    try:
        results = engine.run_all()
        assert isinstance(results, dict)
        assert "ports" in results
        assert "dns" in results
        assert "headers" in results
        assert "sqli" in results
        assert "directories" in results
        assert "ssl" in results
    except Exception:
        pytest.fail("engine.run_all() failed")
