import sqlite3
from .base import get_connection

def get_dashboard_stats():
    """Returns high-level stats for the Manager Dashboard."""
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    try:
        c.execute("SELECT count(*) FROM leads")
        stats['leads_total'] = c.fetchone()[0]
        
        try:
            c.execute("SELECT count(*) FROM campaigns WHERE status='active'")
            stats['active_campaigns'] = c.fetchone()[0]
        except:
             stats['active_campaigns'] = 0

        stats['system_health'] = "Operational"
        return stats
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {'leads_total': 0, 'system_health': 'Error', 'active_campaigns': 0}
    finally:
        conn.close()

def load_table_as_df(table_name):
    """Loads a table into a Pandas DataFrame."""
    conn = get_connection()
    try:
        import pandas as pd
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        return None
    finally:
        conn.close()
