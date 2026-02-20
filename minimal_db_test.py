import sqlite3
import os

DB_PATH = r"C:\sandbox\b2b_outreach_proto\leads_proto.db"

def test_minimal_db():
    print(f"Checking if file exists: {os.path.exists(DB_PATH)}")
    try:
        conn = sqlite3.connect(DB_PATH)
        print("Successfully connected to database.")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM company_profiles")
        count = c.fetchone()[0]
        print(f"Company profiles count: {count}")
        conn.close()
        return True
    except Exception as e:
        print(f"Error during minimal test: {e}")
        return False

if __name__ == "__main__":
    test_minimal_db()
