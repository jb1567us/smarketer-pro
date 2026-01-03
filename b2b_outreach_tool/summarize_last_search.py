import sqlite3
import pandas as pd

conn = sqlite3.connect('leads.db')
query = "SELECT company_name, url, email, qualification_score, relevance_reason FROM leads WHERE source = 'marketing agencies in Austin' ORDER BY created_at DESC"
df = pd.read_sql_query(query, conn)
conn.close()

# Group by domain to see unique companies
df['domain'] = df['url'].apply(lambda x: x.split('//')[-1].split('/')[0] if x else 'Unknown')
summary = df.groupby('domain').first().reset_index()

print(f"Summary of '{len(summary)}' unique domains found in last search:")
print(summary[['domain', 'company_name', 'email']].head(50))
