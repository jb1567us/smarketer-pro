import sqlite3
import datetime

conn = sqlite3.connect('leads.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("Recent searches (distinct sources):")
c.execute("""
    SELECT source, COUNT(*) as count, MAX(created_at) as last_time 
    FROM leads 
    GROUP BY source 
    ORDER BY last_time DESC 
    LIMIT 10
""")
rows = c.fetchall()
for row in rows:
    last_time = datetime.datetime.fromtimestamp(row['last_time']).strftime('%Y-%m-%d %H:%M:%S') if row['last_time'] else 'N/A'
    print(f"Source: {row['source']}, Count: {row['count']}, Last Time: {last_time}")

conn.close()
