import pandas as pd
import sqlite3

conn = sqlite3.connect("db/nifty100.db")

# load peer percentiles
df = pd.read_sql("SELECT * FROM peer_percentiles", conn)

# pivot table → rows = company, columns = metrics
pivot = df.pivot_table(
    index=["company_id", "year"],
    columns="metric",
    values="percentile"
).reset_index()

# save Excel
file_path = "output/peer_comparison.xlsx"

with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
    pivot.to_excel(writer, sheet_name="Peer Comparison", index=False)

    workbook = writer.book
    worksheet = writer.sheets["Peer Comparison"]

    # formats
    green = workbook.add_format({'bg_color': '#C6EFCE'})
    yellow = workbook.add_format({'bg_color': '#FFEB9C'})
    red = workbook.add_format({'bg_color': '#FFC7CE'})

    # apply color scale to percentile columns
    for col_num in range(2, len(pivot.columns)):
        col_letter = chr(65 + col_num)

        worksheet.conditional_format(
            f"{col_letter}2:{col_letter}{len(pivot)+1}",
            {
                'type': '3_color_scale',
                'min_color': "#FFC7CE",
                'mid_color': "#FFEB9C",
                'max_color': "#C6EFCE"
            }
        )

print("peer_comparison.xlsx created!")