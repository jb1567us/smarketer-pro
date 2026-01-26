import sqlite3
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import config
from utils.db_writer import get_db_writer

DB_PATH = os.path.join("data", "leads.db")

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    """Initialize the database tables."""
    # Initialization is heavy and synchronous, fine to keep direct connection for DDL
    conn = get_connection()
    c = conn.cursor()
    
    # Ensure DBWriter is warmed up
    get_db_writer()
    
    # --- WORKSPACES (Multi-Tenancy) ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS workspaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at INTEGER
        );
    ''')
    
    # Migration: Ensure updated_at exists if table was pre-existing
    try:
        c.execute("ALTER TABLE settings ADD COLUMN updated_at INTEGER")
    except:
        pass
    
    # Ensure default workspace exists
    c.execute("INSERT OR IGNORE INTO workspaces (id, name, created_at) VALUES (1, 'Default Workspace', ?)", (int(time.time()),))

    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER DEFAULT 1,
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
            lead_id INTEGER,
            campaign_id INTEGER,
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
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            lead_email TEXT,
            provider_id TEXT, -- e.g. 'mailjet', 'resend'
            provider_msg_id TEXT,
            status TEXT, -- sent, failed, queued
            cost_estimate REAL DEFAULT 0.0,
            metadata_json TEXT,
            timestamp INTEGER
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

    c.execute('''
        CREATE TABLE IF NOT EXISTS link_wheels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            money_site_url TEXT,
            strategy TEXT,
            tier_plan_json TEXT,
            status TEXT DEFAULT 'active',
            created_at INTEGER
        );
    ''')

    # === AFFILIATE MODULE: PUBLISHER SIDE (My Links) ===
    c.execute('''
        CREATE TABLE IF NOT EXISTS my_affiliate_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_name TEXT,
            login_url TEXT,
            username TEXT,
            dashboard_url TEXT,
            notes TEXT,
            created_at INTEGER
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS my_affiliate_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER,
            target_url TEXT,
            cloaked_slug TEXT, -- e.g. 'shopify' for /go/shopify
            category TEXT,
            status TEXT DEFAULT 'active', -- active, broken, paused
            commission_rate TEXT, -- e.g. "20%" or "$50 CPA"
            click_count INTEGER DEFAULT 0,
            last_checked_at INTEGER,
            created_at INTEGER,
            FOREIGN KEY(program_id) REFERENCES my_affiliate_programs(id)
        );
    ''')

    # === AFFILIATE MODULE: BRAND SIDE (My Partners) ===
    c.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            website TEXT,
            social_channels_json TEXT, -- enriched data
            payment_info TEXT, -- PayPal email etc.
            status TEXT DEFAULT 'pending', -- pending, active, suspended
            created_at INTEGER
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS partner_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            contract_type TEXT, -- CPA, RevShare
            terms TEXT, -- e.g "20" for 20%
            start_date INTEGER,
            end_date INTEGER,
            status TEXT DEFAULT 'active',
            FOREIGN KEY(partner_id) REFERENCES partners(id)
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS partner_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            event_type TEXT, -- click, sign_up, sale
            event_value REAL,
            source_url TEXT,
            timestamp INTEGER,
            commission_generated REAL DEFAULT 0,
            status TEXT DEFAULT 'approved', -- approved, reversed
            FOREIGN KEY(partner_id) REFERENCES partners(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS payouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            amount REAL,
            period_start INTEGER,
            period_end INTEGER,
            status TEXT DEFAULT 'due', -- due, paid
            transaction_ref TEXT,
            created_at INTEGER,
            paid_at INTEGER,
            FOREIGN KEY(partner_id) REFERENCES partners(id)
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS strategy_presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            instruction_template TEXT,
            type TEXT DEFAULT 'strategy', -- strategy, task
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
        'company_bio': 'TEXT',
        'notes': 'TEXT'
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

    # Migrate campaign_events
    try:
        c.execute('SELECT lead_id FROM campaign_events LIMIT 1')
    except sqlite3.OperationalError:
        print("Migrating campaign_events: Adding 'lead_id' and 'campaign_id'...")
        c.execute('ALTER TABLE campaign_events ADD COLUMN lead_id INTEGER')
        c.execute('ALTER TABLE campaign_events ADD COLUMN campaign_id INTEGER')

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

    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS custom_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            goal TEXT,
            system_prompt TEXT,
            created_at INTEGER
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS managed_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_name TEXT,
            email TEXT,
            username TEXT,
            password TEXT, -- Encrypted or plain, depending on security requirements
            verification_status TEXT DEFAULT 'pending', -- pending, verified, banned
            proxy_used TEXT,
            created_at INTEGER,
            last_login_at INTEGER,
            metadata TEXT -- JSON for cookies, recovery codes, etc.
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS agent_work_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_role TEXT,
            start_time INTEGER,
            completion_time INTEGER,
            input_task TEXT,
            output_content TEXT,
            tags TEXT,
            created_at INTEGER
        );
    ''')
    
    # Migration for agent_work_products columns
    awp_columns = {
        'start_time': 'INTEGER',
        'completion_time': 'INTEGER', 
        'input_task': 'TEXT',
        'output_content': 'TEXT',
        'tags': 'TEXT',
        'metadata': 'TEXT',
        'artifact_type': 'TEXT'
    }
    # Check if table exists
    try:
        c.execute('SELECT 1 FROM agent_work_products LIMIT 1')
        table_exists = True
    except sqlite3.OperationalError:
        table_exists = False

    if table_exists:
        for col, dtype in awp_columns.items():
            try:
                c.execute(f'SELECT {col} FROM agent_work_products LIMIT 1')
            except sqlite3.OperationalError:
                print(f"Migrating agent_work_products: Adding '{col}' column...")
                try:
                    c.execute(f'ALTER TABLE agent_work_products ADD COLUMN {col} {dtype}')
                except sqlite3.OperationalError as e:
                    print(f"Migration warning for {col}: {e}")

    # Migration for strategy_presets type
    try:
        c.execute("SELECT type FROM strategy_presets LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating strategy_presets: Adding 'type' column...")
        c.execute("ALTER TABLE strategy_presets ADD COLUMN type TEXT DEFAULT 'strategy'")

    # --- Registration Tasks & Macros ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS registration_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            url TEXT,
            details TEXT, -- JSON string
            status TEXT DEFAULT 'pending', -- pending, completed
            created_at INTEGER
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS registration_macros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT UNIQUE,
            steps TEXT, -- JSON string
            created_at INTEGER,
            updated_at INTEGER
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE,
            protocol TEXT, -- http, socks4, socks5
            anonymity TEXT, -- elite, anonymous, transparent
            country TEXT,
            latency REAL,
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0,
            last_used_at INTEGER,
            last_checked_at INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at INTEGER
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS proxy_sources (
            url TEXT PRIMARY KEY,
            type TEXT DEFAULT 'http',
            last_checked INTEGER,
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0,
            consecutive_failures INTEGER DEFAULT 0,
            content_hash TEXT,
            is_active INTEGER DEFAULT 1,
            added_at INTEGER
        );
    ''')
    
    # Migration: proxy_sources new columns
    try:
        c.execute("ALTER TABLE proxy_sources ADD COLUMN content_hash TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE proxy_sources ADD COLUMN consecutive_failures INTEGER DEFAULT 0")
    except:
        pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            tool_call TEXT, -- Name of the tool used, if any
            tool_params TEXT, -- JSON params, if any
            timestamp INTEGER,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
        );
    ''')
    
    # Migration for chat_messages tool columns
    try:
        c.execute("SELECT tool_call FROM chat_messages LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating chat_messages: Adding tool columns...")
        c.execute("ALTER TABLE chat_messages ADD COLUMN tool_call TEXT")
        c.execute("ALTER TABLE chat_messages ADD COLUMN tool_params TEXT")

    # --- Decision Log (Brain Logic) ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS agent_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_role TEXT,
            intent TEXT,
            user_input TEXT,
            tool_selected TEXT,
            tool_params TEXT, -- JSON
            reasoning TEXT,
            timestamp INTEGER
        );
    ''')

    # --- WORKSPACES (Multi-Tenancy) ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS workspaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at INTEGER
        );
    ''')
    
    # Ensure default workspace exists
    c.execute("INSERT OR IGNORE INTO workspaces (id, name, created_at) VALUES (1, 'Default Workspace', ?)", (int(time.time()),))
    
    # Workspace Migration for existing tables
    tables_needing_workspace = ['leads', 'campaigns', 'deals', 'tasks', 'creative_content']
    for table in tables_needing_workspace:
        try:
            c.execute(f'SELECT workspace_id FROM {table} LIMIT 1')
        except sqlite3.OperationalError:
            print(f"Migrating {table}: Adding 'workspace_id' column...")
            try:
                # Default to workspace 1 (Default) for existing data
                c.execute(f'ALTER TABLE {table} ADD COLUMN workspace_id INTEGER DEFAULT 1')
            except Exception as e:
                print(f"Error migrating {table}: {e}")

    c.execute('''
        CREATE TABLE IF NOT EXISTS video_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            optimized_prompt TEXT,
            provider TEXT,
            status TEXT,
            url TEXT,
            job_id TEXT,
            created_at INTEGER
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS influencer_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handle TEXT,
            platform TEXT,
            url TEXT UNIQUE,
            niche TEXT,
            follower_count INTEGER,
            bio_snippet TEXT,
            engagement_rate REAL,
            status TEXT DEFAULT 'new',
            created_at INTEGER,
            metadata TEXT
        );
    ''')
    conn.commit()
    conn.close()

def get_workspaces():
    """Retrieves all available workspaces."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM workspaces ORDER BY id ASC')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def create_workspace(name):
    """Creates a new workspace."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO workspaces (name, created_at) VALUES (?, ?)', (name, int(time.time())))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def create_chat_session(title="New Chat"):
    """Creates a new chat session and returns its ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO chat_sessions (title, created_at) VALUES (?, ?)', (title, int(time.time())))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_chat_message(session_id, role, content, tool_call=None, tool_params=None):
    """Saves a message to a chat session, optionally with tool metadata."""
    conn = get_connection()
    c = conn.cursor()
    import json
    params_json = json.dumps(tool_params) if tool_params else None
    
    c.execute('''
        INSERT INTO chat_messages (session_id, role, content, tool_call, tool_params, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, role, content, tool_call, params_json, int(time.time())))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    """Retrieves all messages for a specific session."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT role, content, tool_call, tool_params FROM chat_messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
    results = []
    for r in c.fetchall():
        d = dict(r)
        # Parse params back to dict if present
        if d.get('tool_params'):
            import json
            try:
                d['tool_params'] = json.loads(d['tool_params'])
            except:
                d['tool_params'] = {}
        results.append(d)
    conn.close()
    return results

def get_chat_sessions(limit=10):
    """Returns the most recent chat sessions."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM chat_sessions ORDER BY created_at DESC LIMIT ?', (limit,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def update_session_title(session_id, title):
    """Updates the title of a chat session."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE chat_sessions SET title = ? WHERE id = ?', (title, session_id))
    conn.commit()
    conn.close()

def save_agent_work_product(agent_role, input_task, output_content, tags=None, start_time=None, completion_time=None, metadata=None, artifact_type="text"):
    """Saves an agent's work product to the database."""
    writer = get_db_writer()
    query = '''
        INSERT INTO agent_work_products (agent_role, start_time, completion_time, input_task, output_content, tags, metadata, artifact_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    params = (agent_role, start_time, completion_time, input_task, output_content, tags_json, meta_json, artifact_type, int(time.time()))
    
    product_id = writer.execute_write(query, params, wait=True)
    return product_id

def get_agent_work_products(agent_role=None, limit=50):
    """Retrieves agent work products, optionally filtered by role."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if agent_role:
        c.execute('SELECT * FROM agent_work_products WHERE agent_role = ? ORDER BY created_at DESC LIMIT ?', (agent_role, limit))
    else:
        c.execute('SELECT * FROM agent_work_products ORDER BY created_at DESC LIMIT ?', (limit,))
        
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

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

def get_current_workspace_id(passed_id=None):
    """Helper to resolve workspace ID from args or session state."""
    if passed_id is not None:
        return passed_id
    try:
        import streamlit as st
        if hasattr(st, 'session_state') and 'active_workspace_id' in st.session_state:
            return st.session_state['active_workspace_id']
    except Exception:
        pass
    return 1 # Default

def add_lead(url, email, source="search", category="default", industry=None, business_type=None, confidence=None, relevance_reason=None, contact_person=None, company_name=None, address=None, phone_number=None, tech_stack=None, qualification_score=None, qualification_reason=None, workspace_id=None):
    """
    Adds a lead to the database. Returns ID if added, None if duplicate.
    """
    writer = get_db_writer()
    ws_id = get_current_workspace_id(workspace_id)
    
    query = '''
        INSERT INTO leads (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, created_at, workspace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    params = (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, int(time.time()), ws_id)
    
    try:
        # DBWriter handles the commit and returns lastrowid
        lead_id = writer.execute_write(query, params, wait=True)
        return lead_id
    except sqlite3.IntegrityError:
        return None
    except Exception as e:
        print(f"Error adding lead: {e}")
        return None

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
    writer = get_db_writer()
    query = '''
        UPDATE leads 
        SET status = 'contacted', contacted_at = ? 
        WHERE email = ?
    '''
    params = (int(time.time()), email)
    writer.execute_write(query, params, wait=True)

def update_enrollment_progress(enrollment_id, next_step_index, next_scheduled_at, status='active'):
    """Updates enrollment status and schedules next touch."""
    writer = get_db_writer()
    query = '''
        UPDATE sequence_enrollments 
        SET current_step_index = ?, last_touch_at = ?, next_scheduled_at = ?, status = ?
        WHERE id = ?
    '''
    params = (next_step_index, int(time.time()), next_scheduled_at, status, enrollment_id)
    writer.execute_write(query, params, wait=True)

def get_leads_by_status(status="new", workspace_id=None):
    """Retrieves all leads with a specific status, returning full details."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row # Access columns by name
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('SELECT * FROM leads WHERE status = ? AND workspace_id = ?', (status, ws_id))
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

def log_campaign_event(email, event_type, template_id=None, event_data=None, lead_id=None, campaign_id=None):
    """Logs an event (sent, open, click) for a lead."""
    writer = get_db_writer()
    query = '''
        INSERT INTO campaign_events (lead_email, template_id, event_type, event_data, timestamp, lead_id, campaign_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    params = (email, template_id, event_type, event_data, int(time.time()), lead_id, campaign_id)
    # Fire and forget for analytics to improve speed
    writer.execute_write(query, params, wait=False)

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

# === LINK WHEEL FUNCTIONS ===

def save_link_wheel(money_site_url, strategy, plan_json):
    """Saves a generated Link Wheel plan."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO link_wheels (money_site_url, strategy, tier_plan_json, created_at)
        VALUES (?, ?, ?, ?)
    ''', (money_site_url, strategy, plan_json, int(time.time())))
    lw_id = c.lastrowid
    conn.commit()
    conn.close()
    return lw_id

def get_link_wheels():
    """Retrieves all saved link wheels."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM link_wheels ORDER BY created_at DESC')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def delete_link_wheel(lw_id):
    """Deletes a link wheel plan."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM link_wheels WHERE id = ?', (lw_id,))
    conn.commit()
    conn.close()

def save_creative_content(agent_type, content_type, title, body, metadata=None, workspace_id=None):
    """Saves generated creative content to the library."""
    conn = get_connection()
    c = conn.cursor()
    import json
    meta_json = json.dumps(metadata) if metadata else "{}"
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('''
        INSERT INTO creative_content (agent_type, content_type, title, body, metadata, created_at, workspace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (agent_type, content_type, title, body, meta_json, int(time.time()), ws_id))
    conn.commit()
    conn.close()
    return True

def get_creative_library(workspace_id=None):
    """Retrieves all saved creative content."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('SELECT * FROM creative_content WHERE workspace_id = ? ORDER BY created_at DESC', (ws_id,))
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

# === AGENT WORK PRODUCTS ===

def save_agent_work(agent_role, content, artifact_type="text", metadata=None):
    """Saves any agent's work product. Wrapper for save_agent_work_product."""
    return save_agent_work_product(
        agent_role=agent_role,
        input_task=f"Work Product ({artifact_type})",
        output_content=content,
        metadata=metadata,
        artifact_type=artifact_type
    )

def get_agent_work(agent_role=None, limit=50):
    """Retrieves recent agent work products."""
    return get_agent_work_products(agent_role, limit)

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

def save_setting(key, value):
    """Saves a global application setting."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    ''', (key, str(value)))
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    """Retrieves a global application setting."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else default




def create_custom_agent(name, role, goal, system_prompt=None):
    """Creates a new custom agent."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO custom_agents (name, role, goal, system_prompt, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, role, goal, system_prompt, int(time.time())))
    agent_id = c.lastrowid
    conn.commit()
    conn.close()
    return agent_id

def get_custom_agents():
    """Retrieves all custom agents."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM custom_agents ORDER BY name ASC')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_custom_agent(agent_id):
    """Retrieves a specific custom agent."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM custom_agents WHERE id = ?', (agent_id,))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

def delete_custom_agent(agent_id):
    """Deletes a custom agent."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM custom_agents WHERE id = ?', (agent_id,))
    conn.commit()
    conn.close()

def create_campaign(name, niche, product_name, product_context, workspace_id=None):
    """Creates a new campaign and returns its ID."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('''
        INSERT INTO campaigns (name, niche, product_name, product_context, created_at, updated_at, workspace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, niche, product_name, product_context, now, now, ws_id))
    campaign_id = c.lastrowid
    conn.commit()
    conn.close()
    return campaign_id

# === STRATEGY PRESETS FUNCTIONS ===

def save_strategy_preset(name, description, instruction_template, type="strategy"):
    """Saves a new strategy preset."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO strategy_presets (name, description, instruction_template, type, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, instruction_template, type, int(time.time())))
    preset_id = c.lastrowid
    conn.commit()
    conn.close()
    return preset_id

def update_strategy_preset(preset_id, name, description, instruction_template):
    """Updates an existing strategy preset."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE strategy_presets 
        SET name = ?, description = ?, instruction_template = ?
        WHERE id = ?
    ''', (name, description, instruction_template, preset_id))
    conn.commit()
    conn.close()

def get_strategy_presets():
    """Retrieves all strategy presets."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM strategy_presets ORDER BY created_at DESC')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_strategy_preset(preset_id):
    """Retrieves a single strategy preset."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM strategy_presets WHERE id = ?', (preset_id,))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

def delete_strategy_preset(preset_id):
    """Deletes a strategy preset."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM strategy_presets WHERE id = ?', (preset_id,))
    conn.commit()
    conn.close()

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

def get_all_campaigns(workspace_id=None):
    """Retrieves all campaigns, ordered by most recent."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('SELECT * FROM campaigns WHERE workspace_id = ? ORDER BY updated_at DESC', (ws_id,))
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

def create_deal(lead_id, title, value, stage='Discovery', probability=20, close_date=None, workspace_id=None):
    """Creates a new deal for a lead."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('''
        INSERT INTO deals (lead_id, title, value, stage, probability, close_date, created_at, workspace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lead_id, title, value, stage, probability, close_date, now, ws_id))
    deal_id = c.lastrowid
    conn.commit()
    conn.close()
    return deal_id

def get_deals(workspace_id=None):
    """Retrieves all deals with lead info."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('''
        SELECT d.*, l.company_name, l.contact_person, l.email
        FROM deals d
        JOIN leads l ON d.lead_id = l.id
        WHERE d.workspace_id = ?
        ORDER BY d.created_at DESC
    ''', (ws_id,))
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

def create_task(lead_id, description, due_date, priority='Medium', task_type='Task', workspace_id=None):
    """Creates a new task for a lead."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('''
        INSERT INTO tasks (lead_id, description, due_date, priority, task_type, status, created_at, workspace_id)
        VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
    ''', (lead_id, description, due_date, priority, task_type, now, ws_id))
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

def get_tasks(status=None, workspace_id=None):
    """Retrieves tasks, optionally filtered by status."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    query = '''
        SELECT t.*, l.company_name, l.contact_person
        FROM tasks t
        LEFT JOIN leads l ON t.lead_id = l.id
        WHERE t.workspace_id = ?
    '''
    params = [ws_id]
    if status:
        query += ' AND t.status = ?'
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

# === MANAGED ACCOUNTS FUNCTIONS ===

def save_managed_account(platform_name, email, username, password, proxy_used=None, metadata=None):
    """Saves a newly created account."""
    conn = get_connection()
    c = conn.cursor()
    import json
    now = int(time.time())
    c.execute('''
        INSERT INTO managed_accounts (platform_name, email, username, password, proxy_used, metadata, created_at, last_login_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (platform_name, email, username, password, proxy_used, json.dumps(metadata or {}), now, now))
    account_id = c.lastrowid
    conn.commit()
    conn.close()
    return account_id

def get_managed_accounts(platform_name=None, status=None):
    """Retrieves managed accounts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = 'SELECT * FROM managed_accounts WHERE 1=1'
    params = []
    
    if platform_name:
        query += ' AND platform_name = ?'
        params.append(platform_name)
    if status:
        query += ' AND verification_status = ?'
        params.append(status)
        
    c.execute(query, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def update_managed_account_status(account_id, status):
    """Updates the status of a managed account."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE managed_accounts SET verification_status = ? WHERE id = ?', (status, account_id))
    conn.commit()
    conn.close()

# === REGISTRATION TASKS & MACROS ===

def add_registration_task(platform, url, details=None):
    """Adds a registration task that requires manual intervention."""
    conn = get_connection()
    c = conn.cursor()
    import json
    details_json = json.dumps(details or {})
    c.execute('''
        INSERT INTO registration_tasks (platform, url, details, created_at)
        VALUES (?, ?, ?, ?)
    ''', (platform, url, details_json, int(time.time())))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_registration_tasks(status='pending'):
    """Retrieves registration tasks."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM registration_tasks WHERE status = ? ORDER BY created_at DESC', (status,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def delete_registration_task(task_id):
    """Deletes a registration task."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM registration_tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def save_registration_macro(platform, steps):
    """Saves or updates a registration macro for a platform."""
    conn = get_connection()
    c = conn.cursor()
    import json
    steps_json = json.dumps(steps)
    now = int(time.time())
    c.execute('''
        INSERT INTO registration_macros (platform, steps, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(platform) DO UPDATE SET
            steps=excluded.steps,
            updated_at=excluded.updated_at
    ''', (platform, steps_json, now, now))
    conn.commit()
    conn.close()

def get_registration_macro(platform):
    """Retrieves a macro for a platform."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM registration_macros WHERE platform = ?', (platform,))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

# === PROXY MANAGEMENT FUNCTIONS ===

def save_proxies(proxy_list, reset=False):
    """
    Saves or updates a list of proxies.
    proxy_list: list of dicts with keys: address, protocol, anonymity, country, latency
    reset: If True, marks all existing proxies as inactive before saving/updating new ones.
    """
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())

    if reset:
        # Deactivate all proxies first, so only the new batch becomes active
        # Or delete them? Deleting is cleaner for "fresh harvest".
        # Let's delete to remove accumulated junk.
        c.execute('DELETE FROM proxies') 

    for p in proxy_list:
        c.execute('''
            INSERT INTO proxies (address, protocol, anonymity, country, latency, last_checked_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(address) DO UPDATE SET
                protocol=COALESCE(excluded.protocol, protocol),
                anonymity=excluded.anonymity, -- Explicitly update tier/anonymity
                country=COALESCE(excluded.country, country),
                latency=excluded.latency,
                last_checked_at=excluded.last_checked_at,
                is_active=1
        ''', (
            p['address'], 
            p.get('protocol', 'http'), 
            p.get('anonymity', 'standard'), # Default to standard
            p.get('country', 'Unknown'),
            p.get('latency', 0),
            now,
            now
        ))
    conn.commit()
    conn.close()

def get_best_proxies(limit=50, min_anonymity=None, min_success_count=0):
    """Retrieves proxies ordered by success rate and latency."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = 'SELECT * FROM proxies WHERE is_active = 1'
    params = []
    if min_anonymity:
        query += ' AND anonymity = ?'
        params.append(min_anonymity)
        
    if min_success_count > 0:
        query += ' AND success_count >= ?'
        params.append(min_success_count)
    
    # Order by success ratio (avoid div zero) and then low latency
    query += ' ORDER BY (CAST(success_count AS REAL) / (success_count + fail_count + 1)) DESC, latency ASC LIMIT ?'
    params.append(limit)
    
    c.execute(query, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def update_proxy_health(address, success=True, latency=None):
    """Updates proxy stats after a check or use."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    
    if success:
        c.execute('''
            UPDATE proxies 
            SET success_count = success_count + 1, 
                fail_count = 0,
                last_used_at = ?, 
                last_checked_at = ?,
                latency = COALESCE(?, latency),
                is_active = 1
            WHERE address = ?
        ''', (now, now, latency, address))
    else:
        c.execute('''
            UPDATE proxies 
            SET fail_count = fail_count + 1, 
                last_checked_at = ?,
                is_active = CASE WHEN fail_count > 10 THEN 0 ELSE 1 END
            WHERE address = ?
        ''', (now, address))
        
    conn.commit()
    conn.close()

def clear_proxies():
    """Wipes the proxy table."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM proxies')
    conn.commit()
    conn.close()

def mark_registration_task_completed(task_id):
    """Marks a registration task as completed."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE registration_tasks SET status = 'completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def save_campaign_state(campaign_id, step):
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


def get_campaign(campaign_id):
    """Retrieves full campaign data."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
    result = c.fetchone()
    conn.close()
    return dict(result) if result else None

def load_data(table):
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * from {table}", conn)
    conn.close()
    return df
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
    res = c.fetchone()
    conn.close()
    return dict(res) if res else None

def get_campaign_state(campaign_id):
    """Retrieves current step."""
    c = get_campaign(campaign_id)
    return c['current_step'] if c else 0

def update_campaign_step(campaign_id, step):
    """Updates step."""
    save_campaign_state(campaign_id, step)

def update_campaign_pain_point(campaign_id, pp_id):
    """Updates selected pain point."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE campaigns SET selected_pain_point_id = ?, updated_at = ? WHERE id = ?', (pp_id, int(time.time()), campaign_id))
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
        pass
    conn.close()

def save_lead_search_result(keyword, result):
    """Saves a raw search result (simplified for now)."""
    # Placeholder if actual logic isn't strictly defined elsewhere
    pass

def get_leads_by_source(source):
    """Retrieves leads filtered by source."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM leads WHERE source = ?', (source,))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_campaign_leads(campaign_id):
    """Retrieves leads associated with a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT l.* FROM leads l
        JOIN campaign_leads cl ON l.id = cl.lead_id
        WHERE cl.campaign_id = ?
    ''', (campaign_id,))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def create_dsr(campaign_id, lead_id, title, content_json, status='draft'):
    """Creates a Digital Sales Room entry."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO digital_sales_rooms (campaign_id, lead_id, title, content_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (campaign_id, lead_id, title, content_json, status, int(time.time())))
    did = c.lastrowid
    conn.commit()
    conn.close()
    return did

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
    """Get all DSRs for a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM digital_sales_rooms WHERE campaign_id = ?', (campaign_id,))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_dsr_by_lead(campaign_id, lead_id):
    """Get DSR for a specific lead in a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM digital_sales_rooms WHERE campaign_id = ? AND lead_id = ?', (campaign_id, lead_id))
    res = c.fetchone()
    conn.close()
    return dict(res) if res else None

def create_sequence(campaign_id, name):
    """Creates a new cadence sequence."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO sequences (campaign_id, name, created_at) VALUES (?, ?, ?)', (campaign_id, name, int(time.time())))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid

def add_sequence_step(sequence_id, step_number, touch_type, delay, content):
    """Adds a step to a sequence."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO sequence_steps (sequence_id, step_number, touch_type, delay_days, content_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (sequence_id, step_number, touch_type, delay, content))
    conn.commit()
    conn.close()

def enroll_lead_in_sequence(lead_id, sequence_id):
    """Enrolls a lead in a sequence."""
    conn = get_connection()
    c = conn.cursor()
    # Check if already enrolled
    c.execute('SELECT id FROM sequence_enrollments WHERE lead_id = ? AND sequence_id = ?', (lead_id, sequence_id))
    if c.fetchone():
        conn.close()
        return # Already enrolled
        
    c.execute('''
        INSERT INTO sequence_enrollments (lead_id, sequence_id, next_scheduled_at, status)
        VALUES (?, ?, ?, 'active')
    ''', (lead_id, sequence_id, int(time.time())))
    conn.commit()
    conn.close()

def get_due_enrollments():
    """Get enrollments ready for next step."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT se.*, s.campaign_id 
        FROM sequence_enrollments se
        JOIN sequences s ON se.sequence_id = s.id
        WHERE se.status = 'active' AND se.next_scheduled_at <= ?
    ''', (int(time.time()),))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_sequence_steps(sequence_id):
    """Get steps for a sequence."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM sequence_steps WHERE sequence_id = ? ORDER BY sequence_id, step_number ASC', (sequence_id,))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_campaign_sequences(campaign_id):
    """Get sequences for a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM sequences WHERE campaign_id = ?', (campaign_id,))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def update_enrollment_progress(enrollment_id, new_step_index, next_run_time, status='active'):
    """Updates enrollment state after processing."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE sequence_enrollments 
        SET current_step_index = ?, next_scheduled_at = ?, status = ?, last_touch_at = ?
        WHERE id = ?
    ''', (new_step_index, next_run_time, status, int(time.time()), enrollment_id))
    conn.commit()
    conn.close()

def load_data(table_name):
    """Loads a table into a Pandas DataFrame."""
    conn = get_connection()
    try:
        import pandas as pd
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        # Return empty DF with basic fallback if possible, or just re-raise
        print(f"Error loading {table_name}: {e}")
        return pd.DataFrame()

def get_deals():
    """Retrieves all deals."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT d.*, l.company_name, l.email 
        FROM deals d 
        JOIN leads l ON d.lead_id = l.id
    ''')
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_tasks(status='pending'):
    """Retrieves tasks by status."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE status = ? ORDER BY due_date ASC', (status,))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def get_scheduled_posts(status='pending'):
    """Retrieves scheduled posts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM scheduled_posts WHERE status = ? ORDER BY scheduled_at ASC', (status,))
    res = c.fetchall()
    conn.close()
    return [dict(r) for r in res]

def save_scheduled_post(agent_type, platforms, content, scheduled_at, metadata=None):
    """Saves a scheduled post."""
    conn = get_connection()
    c = conn.cursor()
    import json
    plats_json = json.dumps(platforms)
    meta_json = json.dumps(metadata) if metadata else "{}"
    
    c.execute('''
        INSERT INTO scheduled_posts (agent_type, platforms, content, scheduled_at, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (agent_type, plats_json, content, scheduled_at, meta_json, int(time.time())))
    conn.commit()
    conn.close()

def delete_scheduled_post(post_id):
    """Deletes a scheduled post."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM scheduled_posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

def save_creative_content(title, body, agent_type="Creative Agent", content_type="text"):
    """Saves creative content."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO creative_content (title, body, agent_type, content_type, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, body, agent_type, content_type, int(time.time())))
    conn.commit()
    conn.close()
def delete_leads_bulk(lead_ids):
    """Deletes multiple leads by their IDs."""
    if not lead_ids:
        return
    conn = get_connection()
    c = conn.cursor()
    placeholders = ','.join(['?'] * len(lead_ids))
    c.execute(f'DELETE FROM leads WHERE id IN ({placeholders})', lead_ids)
    conn.commit()
    conn.close()

def delete_deals_bulk(deal_ids):
    """Deletes multiple deals by their IDs."""
    if not deal_ids:
        return
    conn = get_connection()
    c = conn.cursor()
    placeholders = ','.join(['?'] * len(deal_ids))
    c.execute(f'DELETE FROM deals WHERE id IN ({placeholders})', deal_ids)
    conn.commit()
    conn.close()

# =========================================================================
# SQLALCHEMY ORM SUPPORT (Added for Affiliate System & New Modules)
# =========================================================================
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Use absolute path for SQLite to avoid CWD issues
DB_NAME = 'leads.db'
SQLALCHEMY_DATABASE_URL = f'sqlite:///{DB_NAME}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@contextmanager
def get_db_session():
    '''Provides a transactional scope around a series of operations.'''
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_all_tables():
    '''Creates tables defined by SQLAlchemy models.'''
    # This must be imported by modules defining models (e.g. src.affiliates.models) 
    # BEFORE calling this, so they are registered with Base.metadata
    Base.metadata.create_all(bind=engine)



def log_agent_decision(agent_role, intent, user_input, tool_selected, tool_params, reasoning=''):
    '''Logs an agent decision-making process for audit/debug.'''
    conn = get_connection()
    c = conn.cursor()
    import json
    params_str = json.dumps(tool_params) if isinstance(tool_params, (dict, list)) else str(tool_params)
    
    try:
        c.execute('''
            INSERT INTO agent_decisions (agent_role, intent, user_input, tool_selected, tool_params, reasoning, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (agent_role, intent, user_input, tool_selected, params_str, reasoning, int(time.time())))
        conn.commit()
    except Exception as e:
        print(f'Error logging decision: {e}')
    finally:
        conn.close()

def update_lead(lead_id, data):
    """Updates a lead record with a dictionary of fields."""
    conn = get_connection()
    c = conn.cursor()
    
    fields = []
    values = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        values.append(v)
    
    values.append(lead_id)
    query = f"UPDATE leads SET {', '.join(fields)} WHERE id = ?"
    
    try:
        c.execute(query, tuple(values))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating lead {lead_id}: {e}")
        return False
    finally:
        conn.close()
def duplicate_campaign(campaign_id):
    """Clones a campaign and its core settings."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT name, niche, product_name, product_context, selected_pain_point_id, current_step FROM campaigns WHERE id = ?", (campaign_id,))
        row = c.fetchone()
        if row:
            name, niche, prod, ctx, pp, step = row
            new_name = f"{name} (Copy)"
            c.execute('''
                INSERT INTO campaigns (name, niche, product_name, product_context, selected_pain_point_id, current_step, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'draft', ?)
            ''', (new_name, niche, prod, ctx, pp, step, int(time.time())))
            new_id = c.lastrowid
            conn.commit()
            return new_id
        return None
    except Exception as e:
        print(f"Error duplicating campaign: {e}")
        return None
    finally:
        conn.close()

def update_campaign_status(campaign_id, status):
    """Simple status update for campaigns."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE campaigns SET status = ?, updated_at = ? WHERE id = ?", (status, int(time.time()), campaign_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating campaign status: {e}")
        return False
    finally:
        conn.close()
def delete_dsr(dsr_id):
    """Deletes a DSR record."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM digital_sales_rooms WHERE id = ?", (dsr_id,))
        conn.commit()
    finally:
        conn.close()

def update_dsr_content(dsr_id, content_json):
    """Updates the content of a DSR."""
    conn = get_connection()
    c = conn.cursor()
    import json
    if isinstance(content_json, dict):
        content_json = json.dumps(content_json)
    try:
        c.execute("UPDATE digital_sales_rooms SET content_json = ? WHERE id = ?", (content_json, dsr_id))
        conn.commit()
    finally:
        conn.close()

def save_video_job(prompt, optimized_prompt, provider, status, job_id, url=None):
    """Saves a video generation job to history."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO video_history (prompt, optimized_prompt, provider, status, job_id, url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (prompt, optimized_prompt, provider, status, job_id, url, int(time.time())))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def get_video_history(limit=50):
    """Retrieves recent video generation jobs."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM video_history ORDER BY created_at DESC LIMIT ?', (limit,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def update_video_job_status(job_id, status, url=None):
    """Updates the status and URL of a video job."""
    conn = get_connection()
    c = conn.cursor()
    try:
        if url:
            c.execute("UPDATE video_history SET status = ?, url = ? WHERE job_id = ?", (status, url, job_id))
        else:
            c.execute("UPDATE video_history SET status = ? WHERE job_id = ?", (status, job_id))
        conn.commit()
    finally:
        conn.close()

def update_scheduled_post(post_id, data):
    """Updates a scheduled post record."""
    conn = get_connection()
    c = conn.cursor()
    import json
    fields = []
    values = []
    for k, v in data.items():
        if k == 'platforms' and isinstance(v, list):
             v = json.dumps(v)
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(post_id)
    query = f"UPDATE scheduled_posts SET {', '.join(fields)} WHERE id = ?"
    try:
        c.execute(query, tuple(values))
        conn.commit()
    finally:
        conn.close()

def delete_lead(lead_id):
    """Deletes a lead from the database."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
    finally:
        conn.close()

def get_leads(limit=None):
    """Retrieves leads from the database as a list of dictionaries."""
    conn = get_connection()
    c = conn.cursor()
    try:
        if limit:
            c.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT ?", (limit,))
        else:
            c.execute("SELECT * FROM leads ORDER BY created_at DESC")
        
        columns = [description[0] for description in c.description]
        return [dict(zip(columns, row)) for row in c.fetchall()]
    finally:
        conn.close()

def delete_managed_account(account_id):
    """Deletes a managed account."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM managed_accounts WHERE id = ?", (account_id,))
        conn.commit()
    finally:
        conn.close()

def update_managed_account(account_id, platform, username, status):
    """Updates a managed account."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE managed_accounts SET platform = ?, username = ?, status = ? WHERE id = ?", (platform, username, status, account_id))
        conn.commit()
    finally:
        conn.close()

def save_setting(key, value):
    """Saves a global setting."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)", (key, str(value), int(time.time())))
        conn.commit()
    finally:
        conn.close()

def get_setting(key, default=None):
    """Retrieves a global setting."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = c.fetchone()
        return row[0] if row else default
    finally:
        conn.close()

def get_dashboard_stats():
    """Returns high-level stats for the Manager Dashboard."""
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    try:
        # Leads count
        c.execute("SELECT count(*) FROM leads")
        stats['leads_total'] = c.fetchone()[0]
        
        # Campaigns count
        # Checking if 'campaigns' table exists, otherwise defaulting to 0
        try:
            c.execute("SELECT count(*) FROM campaigns WHERE status='active'")
            stats['active_campaigns'] = c.fetchone()[0]
        except:
             stats['active_campaigns'] = 0

        # System Health (Mock)
        stats['system_health'] = "Operational"
        
        return stats
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {'leads_total': 0, 'system_health': 'Error', 'active_campaigns': 0}
    finally:
        conn.close()
def add_proxy_source(url, source_type='http'):
    """Adds a new proxy source URL."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR IGNORE INTO proxy_sources (url, type, added_at, last_checked) 
            VALUES (?, ?, ?, 0)
        ''', (url, source_type, int(time.time())))
        conn.commit()
    finally:
        conn.close()

def get_proxy_sources(active_only=True):
    """Retrieves proxy sources."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        if active_only:
            c.execute("SELECT * FROM proxy_sources WHERE is_active=1")
        else:
            c.execute("SELECT * FROM proxy_sources")
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def update_proxy_source_status(url, success, content_hash=None, yield_count=0):
    """Updates the status/reputation of a proxy source."""
    conn = get_connection()
    c = conn.cursor()
    try:
        now = int(time.time())
        
        # Get current stats
        c.execute("SELECT consecutive_failures, content_hash, last_checked FROM proxy_sources WHERE url=?", (url,))
        row = c.fetchone()
        if not row: return
        
        curr_fails, last_hash, last_checked = row
        
        # 1. Update Hash & Staleness
        is_stale = False
        if content_hash and last_hash == content_hash:
            # Content hasn't changed. Check time.
            if (now - last_checked) > (7 * 86400): # 7 days
                print(f"[DB] Marking source STALE (Unchanged for 7 days): {url}")
                is_stale = True
        
        # 2. Update Failures
        new_fails = curr_fails
        is_active = 1
        
        if success and yield_count > 0:
            new_fails = 0 # Reset on success
            c.execute("UPDATE proxy_sources SET success_count = success_count + 1 WHERE url=?", (url,))
        else:
            new_fails += 1
            c.execute("UPDATE proxy_sources SET fail_count = fail_count + 1 WHERE url=?", (url,))
            
        if new_fails >= 3 or is_stale:
            is_active = 0
            print(f"[DB] Disabling source (Fails: {new_fails}, Stale: {is_stale}): {url}")
            
        # Execute Update
        c.execute('''
            UPDATE proxy_sources 
            SET last_checked=?, consecutive_failures=?, content_hash=?, is_active=?
            WHERE url=?
        ''', (now, new_fails, content_hash or last_hash, is_active, url))
        
        conn.commit()
    finally:
        conn.close()

# --- Influencer Candidates CRUD ---

def save_influencer_candidate(data):
    """Saves a single influencer candidate."""
    conn = get_connection()
    c = conn.cursor()
    import json
    try:
        # Extract fields
        handle = data.get('handle')
        platform = data.get('platform')
        url = data.get('url')
        niche = data.get('niche')
        try:
             follower_count = int(data.get('expected_followers') or data.get('estimated_followers') or 0)
        except:
             follower_count = 0
             
        bio = data.get('bio_snippet') or data.get('description', '')
        # Only insert if URL is unique
        c.execute('''
            INSERT OR IGNORE INTO influencer_candidates 
            (handle, platform, url, niche, follower_count, bio_snippet, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (handle, platform, url, niche, follower_count, bio, int(time.time()), json.dumps(data)))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def bulk_save_influencers(candidates):
    """Bulk saves a list of influencer dictionaries."""
    conn = get_connection()
    c = conn.cursor()
    import json
    
    count = 0
    try:
        for data in candidates:
            handle = data.get('handle')
            url = data.get('url')
            if not url: continue
            
            platform = data.get('platform', 'unknown')
            niche = data.get('niche', '')
            
            f_val = data.get('estimated_followers', 0)
            try:
                follower_count = int(f_val)
            except:
                follower_count = 0
                
            bio = data.get('bio_snippet', '')
            
            c.execute('''
                INSERT OR IGNORE INTO influencer_candidates 
                (handle, platform, url, niche, follower_count, bio_snippet, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (handle, platform, url, niche, follower_count, bio, int(time.time()), json.dumps(data)))
            if c.rowcount > 0: count += 1
            
        conn.commit()
        return count
    finally:
        conn.close()

def update_influencer_candidate(candidate_id, updates):
    """
    Updates specific fields of an influencer candidate.
    Allowed keys: handle, niche, follower_count, bio_snippet, status, notes
    """
    allowed_keys = ['handle', 'niche', 'follower_count', 'bio_snippet', 'status', 'notes', 'metadata']
    clean_updates = {k: v for k, v in updates.items() if k in allowed_keys}
    
    if not clean_updates:
        return False
        
    conn = get_connection()
    c = conn.cursor()
    
    set_clause = ", ".join([f"{k} = ?" for k in clean_updates.keys()])
    values = list(clean_updates.values())
    values.append(candidate_id)
    
    try:
        c.execute(f"UPDATE influencer_candidates SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return c.rowcount > 0
    except Exception as e:
        print(f"Error updating candidate: {e}")
        return False
    finally:
        conn.close()

def get_influencer_candidates(limit=100, status='new', niche_filter=None):
    """Retrieves influencer candidates."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        query = "SELECT * FROM influencer_candidates WHERE status=?"
        params = [status]
        
        if niche_filter:
            query += " AND niche LIKE ?"
            params.append(f"%{niche_filter}%")
            
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        c.execute(query, tuple(params))
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def update_influencer_status(candidate_id, new_status):
    """Updates the status of a candidate (e.g. new -> selected)."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE influencer_candidates SET status=? WHERE id=?", (new_status, candidate_id))
        conn.commit()
    finally:
        conn.close()

def delete_influencer_candidate(candidate_id):
    """Deletes a candidate."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM influencer_candidates WHERE id=?", (candidate_id,))
        conn.commit()
    finally:
        conn.close()

def get_captcha_settings():
    """
    Retrieves captcha settings from config.yaml (preferred) or database.
    """
    # 1. Config First
    if config.get("captcha"):
        return config["captcha"]
        
    # 2. Database Fallback
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT provider, api_key, enabled FROM captcha_settings WHERE id = 1')
        row = c.fetchone()
        if row:
            return dict(row)
    except Exception as e:
        print(f"DB Error getting captcha settings: {e}")
    finally:
        conn.close()
        
    return None

# --- Influencer Candidates CRUD ---

def add_influencer_candidate(data):
    """
    Adds a new influencer candidate to the database.
    Retuns True if successful, False if duplicate (url) or error.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO influencer_candidates (
                handle, platform, url, niche, follower_count, bio_snippet, 
                engagement_rate, status, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('handle'),
            data.get('platform'),
            data.get('url'),
            data.get('niche'),
            data.get('follower_count', 0),
            data.get('bio_snippet'),
            data.get('engagement_rate', 0.0),
            data.get('status', 'new'),
            int(time.time()),
            data.get('metadata', '{}')
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Duplicate URL
        return False
    except Exception as e:
        print(f"DB Error adding influencer candidate: {e}")
        return False
    finally:
        conn.close()

def get_influencer_candidates(limit=50, status=None, verification_status=None, niche=None, platform=None, offset=0):
    """Retrieves influencer candidates with optional filters."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT * FROM influencer_candidates WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if niche:
        query += " AND niche LIKE ?"
        params.append(f"%{niche}%")

    if platform:
        query += " AND platform = ?"
        params.append(platform)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    try:
        c.execute(query, params)
        results = [dict(r) for r in c.fetchall()]
        return results
    except Exception as e:
        print(f"DB Error getting influencer candidates: {e}")
        return []
    finally:
        conn.close()

def update_influencer_candidate_status(candidate_id, new_status, metadata_update=None):
    """Updates the status and optionally merges new metadata."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE influencer_candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
        
        if metadata_update:
            # Need to fetch existing metadata first to merge? Or just overwrite?
            # Ideally merge, but for simplicity let's require full blob or handle merge in app logic.
            # Here we will just assume the caller handles the merge logic if complex, 
            # or we can do a simple merge if it's a JSON string.
            pass # TODO: Implement metadata merge if needed
            
        conn.commit()
        return True
    except Exception as e:
        print(f"DB Error updating influencer candidate: {e}")
        return False
    finally:
        conn.close()

def delete_influencer_candidates(candidate_ids):
    """Deletes candidates by a list of IDs."""
    if not candidate_ids: return False
    conn = get_connection()
    c = conn.cursor()
    try:
        placeholders = ','.join('?' * len(candidate_ids))
        c.execute(f"DELETE FROM influencer_candidates WHERE id IN ({placeholders})", candidate_ids)
        conn.commit()
        return True
    except Exception as e:
        print(f"DB Error deleting influencer candidates: {e}")
        return False
    finally:
        conn.close()

def get_influencer_stats():
    """Returns counts of candidates grouped by status."""
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    try:
        c.execute("SELECT status, COUNT(*) FROM influencer_candidates GROUP BY status")
        for row in c.fetchall():
            stats[row[0]] = row[1]
    except Exception as e:
        print(f"DB Error getting influencer stats: {e}")
    finally:
        conn.close()

# --- Unified Agent CRUD ---

# 1. Leads (Researcher/Qualifier)
def get_leads(limit=50, workspace_id=None):
    """Retrieves leads for the current workspace."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    c.execute('SELECT * FROM leads WHERE workspace_id = ? ORDER BY created_at DESC LIMIT ?', (ws_id, limit))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def delete_leads(lead_ids):
    """Deletes leads by ID."""
    if not lead_ids: return False
    conn = get_connection()
    c = conn.cursor()
    try:
        placeholders = ','.join('?' * len(lead_ids))
        c.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", lead_ids)
        conn.commit()
        return True
    except Exception as e:
        print(f"DB Error deleting leads: {e}")
        return False
    finally:
        conn.close()

# 2. Creative Content (Copywriter/Designer/Video)
def add_creative_content(data):
    """Adds a creative asset."""
    conn = get_connection()
    c = conn.cursor()
    import json
    try:
        c.execute('''
            INSERT INTO creative_content (
                agent_type, content_type, title, body, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('agent_type'),
            data.get('content_type'),
            data.get('title'),
            data.get('body'),
            data.get('metadata', '{}') if isinstance(data.get('metadata'), str) else json.dumps(data.get('metadata', {})),
            int(time.time())
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"DB Error adding creative content: {e}")
        return False
    finally:
        conn.close()

def get_creative_content(limit=50, agent_type=None):
    """Retrieves creative content, optionally filtered by agent type."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = "SELECT * FROM creative_content"
    params = []
    if agent_type:
        query += " WHERE agent_type = ?"
        params.append(agent_type)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    try:
        c.execute(query, params)
        results = [dict(r) for r in c.fetchall()]
        return results
    except Exception as e:
        print(f"DB Error getting creative content: {e}")
        return []
    finally:
        conn.close()

def delete_creative_content(ids):
    """Deletes creative content by ID."""
    if not ids: return False
    conn = get_connection()
    c = conn.cursor()
    try:
        placeholders = ','.join('?' * len(ids))
        c.execute(f"DELETE FROM creative_content WHERE id IN ({placeholders})", ids)
        conn.commit()
        return True
    except Exception as e:
        print(f"DB Error deleting creative content: {e}")
        return False
    finally:
        conn.close()

# 3. Agent Work Products (Generic)
def get_agent_work_products(limit=50, agent_role=None):
    """Retrieves generic work products."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = "SELECT * FROM agent_work_products"
    params = []
    if agent_role:
        query += " WHERE agent_role = ?"
        params.append(agent_role)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    try:
        c.execute(query, params)
        results = [dict(r) for r in c.fetchall()]
        return results
    except Exception as e:
        print(f"DB Error getting work products: {e}")
        return []
    finally:
        conn.close()

def delete_agent_work_products(ids):
    """Deletes work products by ID."""
    if not ids: return False
    conn = get_connection()
    c = conn.cursor()
    try:
        placeholders = ','.join('?' * len(ids))
        c.execute(f"DELETE FROM agent_work_products WHERE id IN ({placeholders})", ids)
        conn.commit()
        return True
    except Exception as e:
        print(f"DB Error deleting work products: {e}")
        return False
    finally:
        conn.close()
