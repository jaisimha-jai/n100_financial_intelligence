SELECT COUNT(*) FROM companies;

SELECT sector, COUNT(*) 
FROM companies
GROUP BY sector;

SELECT company_id, year, sales
FROM profitandloss
ORDER BY sales DESC
LIMIT 10;

SELECT company_id, year, profit
FROM profitandloss
ORDER BY company_id, year;
SELECT company_id, year, assets
FROM balancesheet
ORDER BY assets DESC
LIMIT 10;
SELECT company_id, year, net_cash
FROM cashflow;
SELECT company_id, date, close_price
FROM stock_prices
LIMIT 20;
SELECT company_id, roe
FROM analysis
ORDER BY roe DESC;

SELECT company_id, year, pe_ratio
FROM financial_ratios
ORDER BY pe_ratio DESC;

SELECT company_id, COUNT(*) 
FROM documents
GROUP BY company_id;