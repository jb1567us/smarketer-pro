import sys
import os

sys.path.append(os.path.abspath("src"))

from analytics_bridge import analytics_bridge
from database import get_campaign_analytics, init_db, get_connection
import time

def verify():
    init_db()
    print("Testing Analytics Bridge...")
    
    # 1. Simulate an event
    import sqlite3
    conn = get_connection()
    c = conn.cursor()
    # Insert dummy lead
    try:
        c.execute("INSERT INTO leads (id, email) VALUES (9999, 'test_analytics@example.com')")
    except sqlite3.IntegrityError:
        pass # Already exists
    conn.commit()
    conn.close()
    
    # Use the bridge
    analytics_bridge.record_event("test_open", campaign_id=101, lead_id=9999, meta="verification_test")
    
    # 2. Check DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM campaign_events WHERE lead_id=9999 AND campaign_id=101 AND event_type='test_open'")
    row = c.fetchone()
    conn.close()
    
    if row:
        print("✅ Analytics event recorded successfully!")
        # Print column names to confirm structure
        # row is tuple, hard to see columns without description
        print(f"Row data: {row}")
    else:
        print("❌ Analytics event FAILED to record.")

if __name__ == "__main__":
    verify()
