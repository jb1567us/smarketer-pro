import sqlite3
import urllib.parse
import os
import sys

# Add src to path to use config
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from config import config

def cleanup_database():
    db_path = "leads.db"
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get blocklist from config
    blocklist = config.get("blocklist", {}).get("domains", [])
    print(f"Cleaning database using {len(blocklist)} blocklisted domains...")

    c.execute("SELECT id, url FROM leads")
    rows = c.fetchall()
    
    ids_to_delete = []
    
    for lead_id, url in rows:
        if not url:
            ids_to_delete.append(lead_id)
            continue
            
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Exact or partial match check
        if any(bl in domain for bl in blocklist):
            ids_to_delete.append(lead_id)
            continue
            
        # Additional junk patterns
        junk_patterns = ['/search?', '/click?', 'adsystem', 'doubleclick', 'itunes.apple.com']
        if any(p in url.lower() for p in junk_patterns):
            ids_to_delete.append(lead_id)
            continue

    if ids_to_delete:
        print(f"Found {len(ids_to_delete)} junk leads to delete.")
        # SQLite limit for parameters is often ~1000, so we chunk deletes
        batch_size = 500
        for i in range(0, len(ids_to_delete), batch_size):
            batch = ids_to_delete[i:i + batch_size]
            placeholders = ','.join(['?'] * len(batch))
            c.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", batch)
        
        conn.commit()
        print(f"Successfully deleted {len(ids_to_delete)} leads.")
    else:
        print("No junk leads found based on current blocklist.")

    conn.close()

if __name__ == "__main__":
    cleanup_database()
