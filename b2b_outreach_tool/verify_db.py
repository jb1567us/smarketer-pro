import sqlite3
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
cols = [description[0] for description in cursor.description]
print(dict(zip(cols, row)))
conn.close()
