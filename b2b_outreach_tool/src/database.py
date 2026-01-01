import sqlite3
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import config

DB_PATH = "leads.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the database tables."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            email TEXT UNIQUE,
            status TEXT DEFAULT 'new', -- new, contacted, error, nurtured
            source TEXT,
            category TEXT,
            industry TEXT,
            business_type TEXT,
            confidence REAL,
            relevance_reason TEXT,
            contact_person TEXT,
            company_name TEXT,
            address TEXT,
            phone_number TEXT,
            created_at INTEGER,
            contacted_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS pain_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niche TEXT,
            pain_point TEXT,
            description TEXT,
            created_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niche TEXT,
            pain_point_id INTEGER,
            stage TEXT, -- intro, value, close
            subject TEXT,
            body_template TEXT,
            created_at INTEGER,
            FOREIGN KEY(pain_point_id) REFERENCES pain_points(id)
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaign_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_email TEXT,
            template_id INTEGER,
            event_type TEXT, -- sent, open, click
            event_data TEXT, -- optional details
            timestamp INTEGER
        );
    ''')
    
    # Simple migration: check if columns exist, if not add them
    # List of new columns to check and add
    new_columns = {
        'category': 'TEXT',
        'industry': 'TEXT',
        'business_type': 'TEXT',
        'confidence': 'REAL',
        'relevance_reason': 'TEXT',
        'contact_person': 'TEXT',
        'company_name': 'TEXT',
        'address': 'TEXT',
        'phone_number': 'TEXT',
        'tech_stack': 'TEXT',
        'qualification_score': 'INTEGER',
        'qualification_reason': 'TEXT'
    }
    
    for col, dtype in new_columns.items():
        try:
            c.execute(f'SELECT {col} FROM leads LIMIT 1')
        except sqlite3.OperationalError:
            print(f"Migrating DB: Adding '{col}' column...")
            try:
                c.execute(f'ALTER TABLE leads ADD COLUMN {col} {dtype}')
            except sqlite3.OperationalError as e:
                print(f"Migration warning for {col}: {e}")

    conn.commit()
    conn.close()

def add_lead(url, email, source="search", category="default", industry=None, business_type=None, confidence=None, relevance_reason=None, contact_person=None, company_name=None, address=None, phone_number=None, tech_stack=None, qualification_score=None, qualification_reason=None):
    """
    Adds a lead to the database. Returns True if added, False if duplicate.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO leads (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, int(time.time())))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def lead_exists(email):
    """Checks if an email already exists in the DB."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT 1 FROM leads WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_contacted(email):
    """Updates the status of a lead to 'contacted'."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE leads 
        SET status = 'contacted', contacted_at = ? 
        WHERE email = ?
    ''', (int(time.time()), email))
    conn.commit()
    conn.close()

def get_leads_by_status(status="new"):
    """Retrieves all leads with a specific status, returning full details."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row # Access columns by name
    c = conn.cursor()
    c.execute('SELECT * FROM leads WHERE status = ?', (status,))
    results = c.fetchall()
    conn.close()
    return [dict(r) for r in results]

def clear_all_leads():
    """Deletes ALL leads from the database. Dangerous!"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM leads')
    conn.commit()
    conn.close()

def delete_leads(lead_ids):
    """Deletes specific leads by ID list."""
    if not lead_ids:
        return
    conn = get_connection()
    c = conn.cursor()
    # Safe parameter substitution for list
    placeholders = ','.join(['?'] * len(lead_ids))
    c.execute(f'DELETE FROM leads WHERE id IN ({placeholders})', lead_ids)
    conn.commit()
    conn.close()

def log_campaign_event(email, event_type, template_id=None, event_data=None):
    """Logs an event (sent, open, click) for a lead."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO campaign_events (lead_email, template_id, event_type, event_data, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (email, template_id, event_type, event_data, int(time.time())))
    conn.commit()
    conn.close()

def save_pain_points(niche, points):
    """Saves a list of pain points for a niche."""
    conn = get_connection()
    c = conn.cursor()
    timestamp = int(time.time())
    for p in points:
        c.execute('''
            INSERT INTO pain_points (niche, pain_point, description, created_at)
            VALUES (?, ?, ?, ?)
        ''', (niche, p['title'], p['description'], timestamp))
    conn.commit()
    conn.close()

def get_pain_points(niche):
    """Retrieves pain points for a niche."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, pain_point, description FROM pain_points WHERE niche = ?', (niche,))
    results = [{'id': r[0], 'title': r[1], 'description': r[2]} for r in c.fetchall()]
    conn.close()
    return results

def save_template(niche, pain_point_id, stage, subject, body):
    """Saves an email template."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO email_templates (niche, pain_point_id, stage, subject, body_template, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (niche, pain_point_id, stage, subject, body, int(time.time())))
    conn.commit()
    conn.close()

def get_templates(niche, stage=None):
    """Retrieves templates for a niche, optionally filtered by stage."""
    conn = get_connection()
    c = conn.cursor()
    if stage:
        c.execute('SELECT id, subject, body_template, pain_point_id FROM email_templates WHERE niche = ? AND stage = ?', (niche, stage))
    else:
        c.execute('SELECT id, subject, body_template, pain_point_id FROM email_templates WHERE niche = ?', (niche,))
    
    results = [{'id': r[0], 'subject': r[1], 'body': r[2], 'pain_point_id': r[3]} for r in c.fetchall()]
    conn.close()
    return results

def get_campaign_analytics():
    """Aggregates campaign events by type."""
    conn = get_connection()
    c = conn.cursor()
    # Count total events by type
    c.execute('''
        SELECT event_type, COUNT(*) 
        FROM campaign_events 
        GROUP BY event_type
    ''')
    results = dict(c.fetchall())
    
    # Get total unique leads targeted (approximate via SENT events)
    c.execute("SELECT COUNT(DISTINCT lead_email) FROM campaign_events WHERE event_type='sent'")
    total_leads_contacted = c.fetchone()[0]
    
    conn.close()
    
    return {
        'sent': results.get('sent', 0),
        'open': results.get('open', 0),
        'click': results.get('click', 0),
        'leads_contacted': total_leads_contacted
    }

def get_daily_engagement(days=30):
    """Aggregates events by day for the last N days."""
    conn = get_connection()
    c = conn.cursor()
    
    # SQLite strftime to group by YYYY-MM-DD
    c.execute(f'''
        SELECT 
            strftime('%Y-%m-%d', timestamp, 'unixepoch') as day,
            event_type,
            COUNT(*)
        FROM campaign_events
        WHERE timestamp > strftime('%s', 'now', '-{days} days')
        GROUP BY day, event_type
        ORDER BY day ASC
    ''')
    
    rows = c.fetchall()
    conn.close()
    
    # Transform into structure: {'2023-10-01': {'sent': 5, 'open': 2}, ...}
    data = {}
    for r in rows:
        day, etype, count = r
        if day not in data:
            data[day] = {'sent': 0, 'open': 0, 'click': 0}
        data[day][etype] = count
        
    return data
