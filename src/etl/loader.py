import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

def load_excel(file_path):
    df = pd.read_excel(file_path, header=1)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    df = df.dropna(how="all")

    return df

def process_all_files():
    for file in RAW_PATH.glob("*.xlsx"):
        print(f"Processing: {file.name}")

        df = load_excel(file)

        output_file = PROCESSED_PATH / f"{file.stem}.csv"
        df.to_csv(output_file, index=False)

if __name__ == "__main__":
    process_all_files()