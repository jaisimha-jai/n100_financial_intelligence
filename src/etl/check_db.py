import sqlite3
conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM companies")
print("Companies count:", cursor.fetchone())
cursor.execute("PRAGMA foreign_key_check")
print("FK check:", cursor.fetchall())
conn.close()