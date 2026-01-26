import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
from database import get_connection as get_db_connection

def fix_sources():
    print("Fixing Proxy Sources...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Delete bad sources
        cursor.execute("DELETE FROM proxy_sources WHERE url LIKE '%test-source%'")
        deleted = cursor.rowcount
        print(f"Deleted {deleted} bad sources.")
        
        # 2. Check if empty
        cursor.execute("SELECT count(*) FROM proxy_sources")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Sources empty. Seeding defaults via ProxyManager...")
            from proxy_manager import proxy_manager
            proxy_manager._sync_sources_from_db() # This seeds defaults if empty
        else:
            print(f"Remaining sources: {count}")
            rows = cursor.execute("SELECT url FROM proxy_sources").fetchall()
            for r in rows:
                print(f" - {r[0]}")
                
        conn.commit()
        conn.close()
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_sources()
