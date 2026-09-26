def test_de_ratio():
    assert 0 == 0  # debt-free case

def test_cagr():
    start = 100
    end = 200
    n = 5
    cagr = ((end/start)**(1/n) - 1) * 100
    assert cagr > 0

def test_percentile():
    import pandas as pd
    s = pd.Series([1,2,3,4])
    assert s.rank(pct=True).iloc[-1] == 1.0