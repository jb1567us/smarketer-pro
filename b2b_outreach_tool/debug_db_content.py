import sqlite3
import json

conn = sqlite3.connect('leads.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT * FROM leads WHERE source = 'marketing agencies in Austin' LIMIT 10")
rows = [dict(r) for r in c.fetchall()]
conn.close()

print(json.dumps(rows, indent=2))
