import sqlite3
import pandas as pd

conn = sqlite3.connect('leads.db')
query = "SELECT * FROM leads WHERE source LIKE '%marketing agencies in Austin%' ORDER BY created_at DESC"
df = pd.read_sql_query(query, conn)
conn.close()

print(f"Found {len(df)} leads for 'marketing agencies in Austin'")
print(df[['id', 'email', 'company_name', 'industry', 'business_type', 'qualification_score', 'relevance_reason']].head(20))
