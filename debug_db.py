import sqlite3
import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from backend.database import DB_PATH
    print(f"Testing DB_PATH: {DB_PATH}")
    print(f"File exists: {os.path.exists(DB_PATH)}")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print(f"Tables in DB: {tables}")
    conn.close()
    print("Direct connection successful.")
except Exception as e:
    print(f"FAILED: {e}")
