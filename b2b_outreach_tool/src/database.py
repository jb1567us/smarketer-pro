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

    c.execute('''
        CREATE TABLE IF NOT EXISTS creative_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_type TEXT, -- Designer, Social Media, etc.
            content_type TEXT, -- image, text, json
            title TEXT,
            body TEXT,
            metadata TEXT, -- JSON string for extra fields
            created_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS wp_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT,
            username TEXT,
            app_password TEXT,
            cpanel_url TEXT,
            cpanel_user TEXT,
            cpanel_pass TEXT,
            created_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS digital_sales_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            lead_id INTEGER,
            site_id INTEGER,
            title TEXT,
            slug TEXT,
            content_json TEXT, -- Stores copy + image URLs
            status TEXT DEFAULT 'draft', -- draft, published
            wp_page_id INTEGER, -- The ID on the WordPress side
            public_url TEXT,
            created_at INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY(lead_id) REFERENCES leads(id),
            FOREIGN KEY(site_id) REFERENCES wp_sites(id)
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sequences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            name TEXT,
            created_at INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sequence_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sequence_id INTEGER,
            step_number INTEGER,
            touch_type TEXT, -- email, linkedin, twitter
            delay_days INTEGER,
            content_json TEXT,
            FOREIGN KEY(sequence_id) REFERENCES sequences(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sequence_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            sequence_id INTEGER,
            current_step_index INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active', -- active, paused, replied, completed
            last_touch_at INTEGER,
            next_scheduled_at INTEGER,
            FOREIGN KEY(lead_id) REFERENCES leads(id),
            FOREIGN KEY(sequence_id) REFERENCES sequences(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            niche TEXT,
            product_name TEXT,
            product_context TEXT,
            selected_pain_point_id INTEGER,
            current_step INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',
            created_at INTEGER,
            updated_at INTEGER,
            FOREIGN KEY(selected_pain_point_id) REFERENCES pain_points(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS campaign_leads (
            campaign_id INTEGER,
            lead_id INTEGER,
            PRIMARY KEY (campaign_id, lead_id),
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            title TEXT,
            value REAL,
            stage TEXT DEFAULT 'Discovery', -- Discovery, Qualification, Proposal, Negotiation, Closed Won, Closed Lost
            probability INTEGER,
            close_date INTEGER,
            created_at INTEGER,
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            description TEXT,
            due_date INTEGER,
            priority TEXT DEFAULT 'Medium', -- Low, Medium, High, Urgent
            task_type TEXT DEFAULT 'Task', -- Call, Email, Meeting, Research, Follow-up
            status TEXT DEFAULT 'pending', -- pending, completed
            created_at INTEGER,
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_type TEXT,
            platforms TEXT, -- JSON list of platforms
            content TEXT,
            scheduled_at INTEGER,
            status TEXT DEFAULT 'pending', -- pending, posted, failed
            metadata TEXT,
            created_at INTEGER
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
        'qualification_reason': 'TEXT',
        'linkedin_url': 'TEXT',
        'twitter_url': 'TEXT',
        'instagram_url': 'TEXT',
        'intent_signals': 'TEXT',
        'company_bio': 'TEXT'
    }
    
    # Check email_templates for campaign_id
    try:
        c.execute('SELECT campaign_id FROM email_templates LIMIT 1')
    except sqlite3.OperationalError:
        print("Migrating email_templates: Adding 'campaign_id' column...")
        c.execute('ALTER TABLE email_templates ADD COLUMN campaign_id INTEGER')
    
    for col, dtype in new_columns.items():
        try:
            c.execute(f'SELECT {col} FROM leads LIMIT 1')
        except sqlite3.OperationalError:
            print(f"Migrating DB: Adding '{col}' column...")
            try:
                c.execute(f'ALTER TABLE leads ADD COLUMN {col} {dtype}')
            except sqlite3.OperationalError as e:
                print(f"Migration warning for {col}: {e}")

    # Migrate tasks table
    task_columns = {
        'priority': 'TEXT DEFAULT "Medium"',
        'task_type': 'TEXT DEFAULT "Task"'
    }
    for col, dtype in task_columns.items():
        try:
            c.execute(f'SELECT {col} FROM tasks LIMIT 1')
        except sqlite3.OperationalError:
            print(f"Migrating Tasks: Adding '{col}' column...")
            c.execute(f'ALTER TABLE tasks ADD COLUMN {col} {dtype}')

    c.execute('''
        CREATE TABLE IF NOT EXISTS platform_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_name TEXT UNIQUE,
            username TEXT,
            password TEXT,
            api_key TEXT,
            meta_json TEXT, -- any extra fields like 'blog_id' or 'client_secret'
            updated_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS captcha_settings (
            id INTEGER PRIMARY KEY DEFAULT 1,
            provider TEXT, -- 'none', '2captcha', 'anticaptcha'
            api_key TEXT,
            enabled INTEGER DEFAULT 0,
            updated_at INTEGER,
            CHECK (id = 1)
        );
    ''')

    conn.commit()
    conn.close()

def save_platform_credential(platform_name, username=None, password=None, api_key=None, meta_json=None):
    """Saves or updates credentials for an SEO platform."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO platform_credentials (platform_name, username, password, api_key, meta_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(platform_name) DO UPDATE SET
            username=excluded.username,
            password=excluded.password,
            api_key=excluded.api_key,
            meta_json=excluded.meta_json,
            updated_at=excluded.updated_at
    ''', (platform_name, username, password, api_key, meta_json, int(time.time())))
    conn.commit()
    conn.close()

def get_platform_credentials(platform_name=None):
    """Retrieves credentials for one or all platforms."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if platform_name:
        c.execute('SELECT * FROM platform_credentials WHERE platform_name = ?', (platform_name,))
        result = c.fetchone()
        conn.close()
        return dict(result) if result else None
    else:
        c.execute('SELECT * FROM platform_credentials')
        results = c.fetchall()
        conn.close()
        return [dict(r) for r in results]

def delete_platform_credential(platform_name):
    """Removes credentials for a platform."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM platform_credentials WHERE platform_name = ?', (platform_name,))
    conn.commit()
    conn.close()

def save_captcha_settings(provider, api_key, enabled):
    """Saves or updates captcha settings."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO captcha_settings (id, provider, api_key, enabled, updated_at)
        VALUES (1, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            provider=excluded.provider,
            api_key=excluded.api_key,
            enabled=excluded.enabled,
            updated_at=excluded.updated_at
    ''', (provider, api_key, 1 if enabled else 0, int(time.time())))
    conn.commit()
    conn.close()

def get_captcha_settings():
    """Retrieves captcha settings."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM captcha_settings WHERE id = 1')
    result = c.fetchone()
    conn.close()
    return dict(result) if result else {"provider": "none", "api_key": "", "enabled": 0}

def add_lead(url, email, source="search", category="default", industry=None, business_type=None, confidence=None, relevance_reason=None, contact_person=None, company_name=None, address=None, phone_number=None, tech_stack=None, qualification_score=None, qualification_reason=None):
    """
    Adds a lead to the database. Returns ID if added, None if duplicate.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO leads (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, int(time.time())))
        lead_id = c.lastrowid
        conn.commit()
        return lead_id
    except sqlite3.IntegrityError:
        return None
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

def get_lead_by_id(lead_id):
    """Retrieves a single lead by its ID."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM leads WHERE id = ?', (lead_id,))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

def update_lead_enrichment(lead_id, enrichment_data):
    """Updates lead with enriched intelligence."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE leads 
        SET linkedin_url = ?, twitter_url = ?, instagram_url = ?, intent_signals = ?, company_bio = ?, tech_stack = ?
        WHERE id = ?
    ''', (
        enrichment_data.get('linkedin_url'),
        enrichment_data.get('twitter_url'),
        enrichment_data.get('instagram_url'),
        enrichment_data.get('intent_signals'),
        enrichment_data.get('company_bio'),
        enrichment_data.get('tech_stack'),
        lead_id
    ))
    conn.commit()
    conn.close()

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

def save_template(niche, pain_point_id, stage, subject, body, campaign_id=None):
    """Saves an email template."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO email_templates (niche, pain_point_id, stage, subject, body_template, campaign_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (niche, pain_point_id, stage, subject, body, campaign_id, int(time.time())))
    conn.commit()
    conn.close()

def get_templates(niche=None, stage=None, campaign_id=None):
    """Retrieves templates for a niche or campaign, optionally filtered by stage."""
    conn = get_connection()
    c = conn.cursor()
    
    query = 'SELECT id, subject, body_template, pain_point_id, campaign_id FROM email_templates WHERE 1=1'
    params = []
    
    if niche:
        query += ' AND niche = ?'
        params.append(niche)
    if stage:
        query += ' AND stage = ?'
        params.append(stage)
    if campaign_id:
        query += ' AND campaign_id = ?'
        params.append(campaign_id)
        
    c.execute(query, params)
    results = [{'id': r[0], 'subject': r[1], 'body': r[2], 'pain_point_id': r[3], 'campaign_id': r[4]} for r in c.fetchall()]
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

def save_creative_content(agent_type, content_type, title, body, metadata=None):
    """Saves generated creative content to the library."""
    conn = get_connection()
    c = conn.cursor()
    import json
    meta_json = json.dumps(metadata) if metadata else "{}"
    c.execute('''
        INSERT INTO creative_content (agent_type, content_type, title, body, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (agent_type, content_type, title, body, meta_json, int(time.time())))
    conn.commit()
    conn.close()
    return True

def get_creative_library():
    """Retrieves all saved creative content."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM creative_content ORDER BY created_at DESC')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def delete_creative_item(item_id):
    """Deletes a specific creative item."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM creative_content WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def save_wp_site(name, url, username, app_password, cp_url=None, cp_user=None, cp_pass=None):
    """Saves or updates a WordPress site's credentials."""
    conn = get_connection()
    c = conn.cursor()
    # Check if a site with this name already exists
    c.execute('SELECT id FROM wp_sites WHERE name = ?', (name,))
    existing = c.fetchone()
    
    if existing:
        c.execute('''
            UPDATE wp_sites 
            SET url = ?, username = ?, app_password = ?, cpanel_url = ?, cpanel_user = ?, cpanel_pass = ?
            WHERE name = ?
        ''', (url, username, app_password, cp_url, cp_user, cp_pass, name))
    else:
        c.execute('''
            INSERT INTO wp_sites (name, url, username, app_password, cpanel_url, cpanel_user, cpanel_pass, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, url, username, app_password, cp_url, cp_user, cp_pass, int(time.time())))
    
    conn.commit()
    conn.close()
    return True

def get_wp_sites():
    """Retrieves all saved WordPress sites."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM wp_sites ORDER BY name ASC')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def delete_wp_site(site_id):
    """Deletes a saved WordPress site."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM wp_sites WHERE id = ?', (site_id,))
    conn.commit()
    conn.close()

# === CAMPAIGN MANAGEMENT FUNCTIONS ===

def create_campaign(name, niche, product_name, product_context):
    """Creates a new campaign and returns its ID."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    c.execute('''
        INSERT INTO campaigns (name, niche, product_name, product_context, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, niche, product_name, product_context, now, now))
    campaign_id = c.lastrowid
    conn.commit()
    conn.close()
    return campaign_id

def update_campaign_step(campaign_id, step):
    """Updates the current step of a campaign."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE campaigns 
        SET current_step = ?, updated_at = ?
        WHERE id = ?
    ''', (step, int(time.time()), campaign_id))
    conn.commit()
    conn.close()

def update_campaign_pain_point(campaign_id, pain_point_id):
    """Updates the selected pain point for a campaign."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE campaigns 
        SET selected_pain_point_id = ?, updated_at = ?
        WHERE id = ?
    ''', (pain_point_id, int(time.time()), campaign_id))
    conn.commit()
    conn.close()

def get_campaign(campaign_id):
    """Retrieves full details of a single campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

def get_all_campaigns():
    """Retrieves all campaigns, ordered by most recent."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM campaigns ORDER BY updated_at DESC')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def delete_campaign(campaign_id):
    """Deletes a campaign and its associated leads/templates."""
    conn = get_connection()
    c = conn.cursor()
    # 1. Delete lead associations
    c.execute('DELETE FROM campaign_leads WHERE campaign_id = ?', (campaign_id,))
    # 2. Delete templates
    c.execute('DELETE FROM email_templates WHERE campaign_id = ?', (campaign_id,))
    # 3. Delete campaign
    c.execute('DELETE FROM campaigns WHERE id = ?', (campaign_id,))
    conn.commit()
    conn.close()

def add_lead_to_campaign(campaign_id, lead_id):
    """Links a lead to a campaign."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO campaign_leads (campaign_id, lead_id) VALUES (?, ?)', (campaign_id, lead_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already linked
    finally:
        conn.close()

def get_campaign_leads(campaign_id):
    """Retrieves all leads associated with a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT l.* 
        FROM leads l
        JOIN campaign_leads cl ON l.id = cl.lead_id
        WHERE cl.campaign_id = ?
    ''', (campaign_id,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

# === DIGITAL SALES ROOM (DSR) FUNCTIONS ===

def create_dsr(campaign_id, lead_id, title, content_json, site_id=None):
    """Creates a new Digital Sales Room entry."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO digital_sales_rooms (campaign_id, lead_id, site_id, title, content_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (campaign_id, lead_id, site_id, title, content_json, int(time.time())))
    dsr_id = c.lastrowid
    conn.commit()
    conn.close()
    return dsr_id

def update_dsr_wp_info(dsr_id, wp_page_id, public_url, status='published'):
    """Updates DSR with WordPress deployment info."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE digital_sales_rooms 
        SET wp_page_id = ?, public_url = ?, status = ?
        WHERE id = ?
    ''', (wp_page_id, public_url, status, dsr_id))
    conn.commit()
    conn.close()

def get_dsrs_for_campaign(campaign_id):
    """Returns all DSRs associated with a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM digital_sales_rooms WHERE campaign_id = ?', (campaign_id,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_dsr_by_lead(campaign_id, lead_id):
    """Gets a DSR for a specific lead in a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM digital_sales_rooms WHERE campaign_id = ? AND lead_id = ?', (campaign_id, lead_id))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

# === CADENCE / SEQUENCE FUNCTIONS ===

def create_sequence(campaign_id, name):
    """Creates a new outreach sequence."""
    conn = get_connection()
    c = conn.cursor()
    import time
    c.execute('INSERT INTO sequences (campaign_id, name, created_at) VALUES (?, ?, ?)',
              (campaign_id, name, int(time.time())))
    seq_id = c.lastrowid
    conn.commit()
    conn.close()
    return seq_id

def add_sequence_step(sequence_id, step_number, touch_type, delay_days, content_json):
    """Adds a step to a sequence."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO sequence_steps (sequence_id, step_number, touch_type, delay_days, content_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (sequence_id, step_number, touch_type, delay_days, content_json))
    conn.commit()
    conn.close()

def enroll_lead_in_sequence(lead_id, sequence_id):
    """Enrolls a lead in a sequence and schedules the first touch."""
    conn = get_connection()
    c = conn.cursor()
    import time
    now = int(time.time())
    c.execute('''
        INSERT INTO sequence_enrollments (lead_id, sequence_id, current_step_index, status, next_scheduled_at)
        VALUES (?, ?, 0, 'active', ?)
    ''', (lead_id, sequence_id, now))
    conn.commit()
    conn.close()

def get_due_enrollments():
    """Returns all enrollments that are due for a touch."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    import time
    c.execute('''
        SELECT se.*, l.email, l.contact_person, l.company_name
        FROM sequence_enrollments se
        JOIN leads l ON se.lead_id = l.id
        WHERE se.status = 'active' AND se.next_scheduled_at <= ?
    ''', (int(time.time()),))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_sequence_steps(sequence_id):
    """Returns all steps for a sequence, ordered by step number."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM sequence_steps WHERE sequence_id = ? ORDER BY step_number ASC', (sequence_id,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_campaign_sequences(campaign_id):
    """Returns all sequences for a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM sequences WHERE campaign_id = ?', (campaign_id,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def update_enrollment_progress(enrollment_id, next_step_index, next_scheduled_at, status='active'):
    """Updates enrollment status and schedules next touch."""
    conn = get_connection()
    c = conn.cursor()
    import time
    c.execute('''
        UPDATE sequence_enrollments 
        SET current_step_index = ?, last_touch_at = ?, next_scheduled_at = ?, status = ?
        WHERE id = ?
    ''', (next_step_index, int(time.time()), next_scheduled_at, status, enrollment_id))
    conn.commit()
    conn.close()

# === CRM / DEAL MANAGEMENT FUNCTIONS ===

def create_deal(lead_id, title, value, stage='Discovery', probability=20, close_date=None):
    """Creates a new deal for a lead."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    c.execute('''
        INSERT INTO deals (lead_id, title, value, stage, probability, close_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (lead_id, title, value, stage, probability, close_date, now))
    deal_id = c.lastrowid
    conn.commit()
    conn.close()
    return deal_id

def get_deals():
    """Retrieves all deals with lead info."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT d.*, l.company_name, l.contact_person, l.email
        FROM deals d
        JOIN leads l ON d.lead_id = l.id
        ORDER BY d.created_at DESC
    ''')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def update_deal_stage(deal_id, stage, probability):
    """Updates the stage and probability of a deal."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE deals 
        SET stage = ?, probability = ?
        WHERE id = ?
    ''', (stage, probability, deal_id))
    conn.commit()
    conn.close()

# === TASK MANAGEMENT FUNCTIONS ===

def create_task(lead_id, description, due_date, priority='Medium', task_type='Task'):
    """Creates a new task for a lead."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    c.execute('''
        INSERT INTO tasks (lead_id, description, due_date, priority, task_type, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    ''', (lead_id, description, due_date, priority, task_type, now))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return task_id

def update_task(task_id, **kwargs):
    """Updates task fields dynamically."""
    if not kwargs:
        return
    conn = get_connection()
    c = conn.cursor()
    
    fields = []
    params = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        params.append(value)
    
    params.append(task_id)
    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    c.execute(query, params)
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Deletes a task by ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_tasks(status=None):
    """Retrieves tasks, optionally filtered by status."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = '''
        SELECT t.*, l.company_name, l.contact_person
        FROM tasks t
        LEFT JOIN leads l ON t.lead_id = l.id
    '''
    params = []
    if status:
        query += ' WHERE t.status = ?'
        params.append(status)
    query += ' ORDER BY t.due_date ASC'
    
    c.execute(query, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def mark_task_completed(task_id):
    """Marks a task as completed."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
# === SOCIAL SCHEDULER FUNCTIONS ===

def save_scheduled_post(agent_type, platforms, content, scheduled_at, metadata=None):
    """Saves a post to be scheduled for social media."""
    conn = get_connection()
    c = conn.cursor()
    import json
    now = int(time.time())
    c.execute('''
        INSERT INTO scheduled_posts (agent_type, platforms, content, scheduled_at, status, metadata, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?, ?)
    ''', (agent_type, json.dumps(platforms), content, scheduled_at, json.dumps(metadata or {}), now))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id

def get_scheduled_posts(status=None):
    """Retrieves scheduled posts, optionally filtered by status."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = 'SELECT * FROM scheduled_posts'
    params = []
    if status:
        query += ' WHERE status = ?'
        params.append(status)
    query += ' ORDER BY scheduled_at ASC'
    
    c.execute(query, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def delete_scheduled_post(post_id):
    """Deletes a scheduled post."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM scheduled_posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
