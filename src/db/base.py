import sqlite3
import os
import time
import sys
from utils.db_writer import get_db_writer

# Find project root (up 2 levels from src/db/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "leads.db")

def get_connection():
    """Returns a valid SQLite connection with proper timeouts."""
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
             
    # Ensure directory permissions (Docker fix)
    if os.path.exists(DB_PATH):
        if not os.access(DB_PATH, os.R_OK | os.W_OK):
            try:
                os.chmod(DB_PATH, 0o666)
            except: pass

    conn = sqlite3.connect(DB_PATH, timeout=60, check_same_thread=False)
    return conn

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

def init_db():
    """Complete Schema Initialization. Safe to run multiple times."""
    conn = get_connection()
    c = conn.cursor()
    
    # Ensure DBWriter is warmed up
    get_db_writer()
    
    # --- WORKSPACES ---
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
    
    # Migrations
    try: c.execute("ALTER TABLE settings ADD COLUMN updated_at INTEGER")
    except: pass
    
    c.execute("INSERT OR IGNORE INTO workspaces (id, name, created_at) VALUES (1, 'Default Workspace', ?)", (int(time.time()),))

    # --- LEADS & CORE CRM ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER DEFAULT 1,
            url TEXT,
            email TEXT UNIQUE,
            status TEXT DEFAULT 'new',
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
            tech_stack TEXT,
            qualification_score INTEGER,
            qualification_reason TEXT,
            linkedin_url TEXT,
            twitter_url TEXT,
            instagram_url TEXT,
            intent_signals TEXT,
            company_bio TEXT,
            notes TEXT,
            created_at INTEGER,
            contacted_at INTEGER
        );
    ''')
    
    # --- CAMPAIGNS & OUTREACH ---
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
            stage TEXT,
            subject TEXT,
            body_template TEXT,
            campaign_id INTEGER,
            created_at INTEGER,
            FOREIGN KEY(pain_point_id) REFERENCES pain_points(id)
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER DEFAULT 1,
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
        CREATE TABLE IF NOT EXISTS campaign_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_email TEXT,
            lead_id INTEGER,
            campaign_id INTEGER,
            template_id INTEGER,
            event_type TEXT,
            event_data TEXT,
            timestamp INTEGER
        );
    ''')

    # --- AGENT LOGS & DECISIONS ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS agent_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_role TEXT,
            intent TEXT,
            user_input TEXT,
            tool_selected TEXT,
            tool_params TEXT,
            reasoning TEXT,
            timestamp INTEGER
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
            metadata TEXT,
            artifact_type TEXT,
            created_at INTEGER
        );
    ''')

    # --- CHAT SESSIONS ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at INTEGER
        );
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            tool_call TEXT,
            tool_params TEXT,
            timestamp INTEGER,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
        );
    ''')

    # --- PROXIES ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE,
            protocol TEXT,
            anonymity TEXT,
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

    # --- PARTNERS & AFFILIATES ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            website TEXT,
            social_channels_json TEXT,
            payment_info TEXT,
            status TEXT DEFAULT 'pending',
            created_at INTEGER
        );
    ''')

    conn.commit()
    conn.close()

# --- SQLALCHEMY SUPPORT ---
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

SQLALCHEMY_DATABASE_URL = f'sqlite:///{DB_PATH}'
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db_session():
    """Provides a transactional scope around a series of operations."""
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
    """Creates tables defined by SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)
