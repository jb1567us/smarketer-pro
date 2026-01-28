import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

DB_PATH = os.path.join(os.getcwd(), 'data', 'leads.db')

def wipe_proxies():
    print(f"Connecting to database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check count before
        cursor.execute("SELECT COUNT(*) FROM proxies")
        count_before = cursor.fetchone()[0]
        print(f"Current Proxy Count: {count_before}")
        
        if count_before > 0:
            print("Wiping all proxies...")
            cursor.execute("DELETE FROM proxies")
            conn.commit()
            print("✅ Proxies table cleared.")
            
            # Reset metadata text logic if needed, but usually just rows is enough
        else:
            print("⚠️ Table already empty.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    wipe_proxies()
