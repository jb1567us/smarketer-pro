import sqlite3
import time
import datetime

conn = sqlite3.connect('leads.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("Last 10 leads added:")
c.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 10")
rows = c.fetchall()
for row in rows:
    created_at = datetime.datetime.fromtimestamp(row['created_at']).strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else 'N/A'
    print(f"ID: {row['id']}, Email: {row['email']}, Source: {row['source']}, Created At: {created_at}, Company: {row['company_name']}")

conn.close()
