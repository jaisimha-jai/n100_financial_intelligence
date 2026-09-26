from src.etl.normaliser import normalize_year, normalize_ticker
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def test_normalize_year():
    assert normalize_year("2022") == 2022
    assert normalize_year("2022-03") == 2022
    assert normalize_year(None) is None


def test_normalize_ticker():
    assert normalize_ticker("infy") == "INFY"
    assert normalize_ticker(" tcs ") == "TCS"
    assert normalize_ticker(None) is None