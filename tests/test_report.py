import pytest
import os
from src.scanner.report import ReportGenerator

def test_report_initialization():
    report = ReportGenerator("example.com", {"test": "data"})
    assert report.target == "example.com"

def test_json_report_creation():
    report = ReportGenerator("example.com", {"key": "value"})
    filename = report.save_json(directory="test_reports")

    assert os.path.exists(filename)
    os.remove(filename)

def test_txt_report_creation():
    report = ReportGenerator("example.com", {"key": "value"})
    filename = report.save_txt(directory="test_reports")

    assert os.path.exists(filename)
    os.remove(filename)
