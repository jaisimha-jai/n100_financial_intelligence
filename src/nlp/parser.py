import pandas as pd
import re
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

INPUT_FILE = os.path.join(BASE_DIR, "data", "analysis.xlsx")
OUTPUT_FILE = os.path.join(BASE_DIR, "output", "analysis_parsed.csv")
FAIL_FILE = os.path.join(BASE_DIR, "output", "parse_failures.csv")

os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)


def parse_text(text):
    pattern = r"(\d+)\s*Years?:?\s*([\d.]+)%"
    match = re.search(pattern, str(text))

    if match:
        years = int(match.group(1))
        value = float(match.group(2))
        return years, value
    return None, None


def run_parser():

    try:
        df = pd.read_excel(INPUT_FILE)
    except:
        print("analysis.xlsx not found")
        return

    parsed_rows = []
    failed_rows = []

    target_cols = [
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe"
    ]

    for _, row in df.iterrows():
        company_id = row.get("company_id")

        for col in target_cols:
            text = row.get(col)

            years, value = parse_text(text)

            if years is not None:
                parsed_rows.append({
                    "company_id": company_id,
                    "metric_type": col,
                    "period_years": years,
                    "value_pct": value
                })
            else:
                failed_rows.append({
                    "company_id": company_id,
                    "metric_type": col,
                    "raw_text": text
                })

    pd.DataFrame(parsed_rows).to_csv(OUTPUT_FILE, index=False)
    pd.DataFrame(failed_rows).to_csv(FAIL_FILE, index=False)

    print("analysis_parsed.csv created")
    print("parse_failures.csv created")


if __name__ == "__main__":
    run_parser()