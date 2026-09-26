import pandas as pd
from pathlib import Path
import os

PROCESSED_PATH = Path("data/processed")
OUTPUT_PATH = Path("output")

def validate_file(file_path):
    df = pd.read_csv(file_path)
    errors = []

    if df.isnull().sum().sum() > 0:
        errors.append(f"{file_path.name}: Missing values found")

    if df.duplicated().sum() > 0:
        errors.append(f"{file_path.name}: Duplicate rows found")

    # DQ-03: Empty file
    if df.shape[0] == 0:
        errors.append(f"{file_path.name}: Empty file")

    return errors


def run_validation():
    all_errors = []

    for file in PROCESSED_PATH.glob("*.csv"):
        print(f"Validating: {file.name}")
        errors = validate_file(file)
        all_errors.extend(errors)

    output_file = OUTPUT_PATH / "validation_failures.csv"

    if os.path.exists(output_file):
        os.remove(output_file)

    pd.DataFrame(all_errors, columns=["error"]).to_csv(output_file, index=False)

    print(f"\nValidation complete. Report saved to {output_file}")


if __name__ == "__main__":
    run_validation()