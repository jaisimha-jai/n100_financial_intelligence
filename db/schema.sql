PRAGMA foreign_keys = ON;

-- 1. Companies
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    name TEXT,
    ticker TEXT,
    sector TEXT
);

-- 2. Profit & Loss
CREATE TABLE profitandloss (
    company_id INTEGER,
    year INTEGER,
    revenue REAL,
    profit REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- 3. Balance Sheet
CREATE TABLE balancesheet (
    company_id INTEGER,
    year INTEGER,
    assets REAL,
    liabilities REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE cashflow (
    company_id INTEGER,
    year INTEGER,
    cashflow REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE stock_prices (
    company_id INTEGER,
    date TEXT,
    close_price REAL,
    PRIMARY KEY (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);