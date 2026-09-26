def normalize_year(year):
    try:
        year = str(year)
        return int(year[:4])
    except:
        return None


def normalize_ticker(ticker):
    if ticker is None:
        return None
    return str(ticker).strip().upper()