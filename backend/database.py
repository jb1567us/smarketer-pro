import sqlite3
import os
import time
from typing import List, Dict, Any

# Database filename
DB_NAME = "leads_proto.db"

def get_connection():
    # Priority 1: Check Docker mount folder path (Best Practice)
    docker_data_path = os.path.join("/app/data", DB_NAME)
    if os.path.exists("/app/data"):
        return sqlite3.connect(docker_data_path, check_same_thread=False)
        
    # Priority 2: Check current working directory
    cwd_path = os.path.join(os.getcwd(), DB_NAME)
    if os.path.exists(cwd_path):
        return sqlite3.connect(cwd_path, check_same_thread=False)

    # Priority 3: Check relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rel_path = os.path.join(base_dir, DB_NAME)
    
    # Final fallback: create in standard location
    return sqlite3.connect(rel_path, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Social Posts Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            platforms TEXT,
            content TEXT,
            scheduled_ts INTEGER,
            status TEXT DEFAULT 'pending',
            created_at INTEGER
        )
    ''')
    
    # Affiliate Programs Table (My Programs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS my_affiliate_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_name TEXT UNIQUE,
            login_url TEXT,
            username TEXT,
            dashboard_url TEXT,
            notes TEXT,
            created_at INTEGER
        )
    ''')
    
    # Affiliate Links Table (My Links)
    c.execute('''
        CREATE TABLE IF NOT EXISTS my_affiliate_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER,
            target_url TEXT,
            cloaked_slug TEXT UNIQUE,
            category TEXT,
            commission_rate TEXT,
            click_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            last_checked_at INTEGER,
            created_at INTEGER,
            FOREIGN KEY(program_id) REFERENCES my_affiliate_programs(id)
        )
    ''')
    
    # Partners Table (Brand Mode)
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
        )
    ''')
    
    # Partner Contracts Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS partner_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            contract_type TEXT,
            terms TEXT,
            status TEXT DEFAULT 'active',
            start_date INTEGER,
            end_date INTEGER,
            FOREIGN KEY(partner_id) REFERENCES partners(id)
        )
    ''')
    
    # Partner Events Table (Clicks/Sales)
    c.execute('''
        CREATE TABLE IF NOT EXISTS partner_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            event_type TEXT,
            event_value REAL,
            source_url TEXT,
            commission_generated REAL,
            timestamp INTEGER,
            FOREIGN KEY(partner_id) REFERENCES partners(id)
        )
    ''')
    
    # Digital Sales Rooms (DSR) Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS digital_sales_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            campaign_id INTEGER,
            title TEXT,
            content_json TEXT,
            status TEXT DEFAULT 'draft',
            public_url TEXT,
            created_at INTEGER,
            FOREIGN KEY(lead_id) REFERENCES leads(id),
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
        )
    ''')
    
    # WordPress Sites Table (Deployment Targets)
    c.execute('''
        CREATE TABLE IF NOT EXISTS wordpress_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            username TEXT,
            application_password TEXT,
            status TEXT DEFAULT 'active',
            created_at INTEGER
        )
    ''')
    
    # Creative Items Table (Image Library)
    c.execute('''
        CREATE TABLE IF NOT EXISTS creative_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            title TEXT,
            content_url TEXT,
            local_path TEXT,
            metadata TEXT,
            created_at INTEGER
        )
    ''')
    
    # Video History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS video_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            optimized_prompt TEXT,
            provider TEXT,
            status TEXT,
            job_id TEXT,
            url TEXT,
            created_at INTEGER
        )
    ''')
    
    # SEO Audits Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS seo_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            score INTEGER,
            metrics_json TEXT,
            report_json TEXT,
            created_at INTEGER
        )
    ''')
    
    # Keyword Reports Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS keyword_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            results_json TEXT,
            created_at INTEGER
        )
    ''')

    # Company Profiles Table (Pillar 3: Content Layer)
    c.execute('''
        CREATE TABLE IF NOT EXISTS company_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            niche TEXT,
            city TEXT,
            review_count INTEGER,
            avg_rating REAL,
            reputation_score REAL,
            metadata_json TEXT,
            last_enriched INTEGER,
            created_at INTEGER
        )
    ''')

    # Market Events Table (MarketMind)
    c.execute('''
        CREATE TABLE IF NOT EXISTS market_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niche TEXT,
            source TEXT,
            headline TEXT,
            summary TEXT,
            sentiment TEXT,
            strategic_hook TEXT,
            timestamp INTEGER
        )
    ''')

    # Video Jobs Table (Phase 6)
    c.execute('''
        CREATE TABLE IF NOT EXISTS video_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            lead_name TEXT,
            script TEXT,
            status TEXT,
            video_url TEXT,
            timestamp INTEGER
        )
    ''')

    # CRM Sync Logs (Phase 7)
    c.execute('''
        CREATE TABLE IF NOT EXISTS crm_sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            provider TEXT,
            external_id TEXT,
            status TEXT,
            timestamp INTEGER
        )
    ''')

    # Escalation Protocol (Phase 8)
    c.execute('''
        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_type TEXT,
            risk_level TEXT,
            context_json TEXT,
            status TEXT,
            approved_by TEXT,
            timestamp INTEGER
        )
    ''')

    # Campaigns Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            niche TEXT,
            product_name TEXT,
            product_context TEXT,
            status TEXT DEFAULT 'active',
            created_at INTEGER
        )
    ''')

    # Leads Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            company_name TEXT,
            source TEXT,
            status TEXT DEFAULT 'new',
            url TEXT,
            contact_person TEXT,
            tech_stack TEXT,
            campaign_id INTEGER,
            confidence REAL,
            notes TEXT,
            intent_signals TEXT,
            created_at INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
        )
    ''')

    # Content Assets (Phase 9)
    c.execute('''
        CREATE TABLE IF NOT EXISTS content_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            asset_type TEXT,
            layout_json TEXT,
            status TEXT,
            timestamp INTEGER
        )
    ''')
    
    # Chat Sessions Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at INTEGER
        )
    ''')

    # Chat Messages Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp INTEGER,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_chat_sessions() -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM chat_sessions ORDER BY created_at DESC").fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res

def get_chat_history(session_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,)).fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res

def add_message(session_id: int, role: str, content: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, int(time.time()))
    )
    conn.commit()
    conn.close()
    import json
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO scheduled_posts (source, platforms, content, scheduled_ts, created_at) VALUES (?, ?, ?, ?, ?)",
        (source, json.dumps(platforms), content, scheduled_ts, int(time.time()))
    )
    conn.commit()
    conn.close()

def get_scheduled_posts(status: str = 'pending') -> List[Dict[str, Any]]:
    import json
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM scheduled_posts WHERE status = ? ORDER BY scheduled_ts ASC", (status,))
    rows = [dict(row) for row in c.fetchall()]
    for row in rows:
        try:
            row['platforms'] = json.loads(row['platforms'])
        except:
            row['platforms'] = []
    conn.close()
    return rows

def delete_scheduled_post(post_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM scheduled_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def update_scheduled_post(post_id: int, update_data: Dict[str, Any]):
    conn = get_connection()
    keys = ", ".join([f"{k} = ?" for k in update_data.keys()])
    values = list(update_data.values())
    values.append(post_id)
    conn.execute(f"UPDATE scheduled_posts SET {keys} WHERE id = ?", values)
    conn.commit()
    conn.close()

def save_creative_content(type: str, title: str, content_url: str, local_path: str = None, metadata: str = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO creative_items (type, title, content_url, local_path, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (type, title, content_url, local_path, metadata, int(time.time()))
    )
    conn.commit()
    conn.close()

def get_creative_library(type_filter: str = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    if type_filter:
        rows = conn.execute("SELECT * FROM creative_items WHERE type = ? ORDER BY created_at DESC", (type_filter,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM creative_items ORDER BY created_at DESC").fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res

def save_video_job(prompt: str, optimized_prompt: str, provider: str, status: str, job_id: str = None, url: str = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO video_history (prompt, optimized_prompt, provider, status, job_id, url, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (prompt, optimized_prompt, provider, status, job_id, url, int(time.time()))
    )
    conn.commit()
    conn.close()

def get_video_history() -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM video_history ORDER BY created_at DESC").fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res

def save_seo_audit(url: str, score: int, metrics: Dict, report: Dict):
    conn = get_connection()
    conn.execute(
        "INSERT INTO seo_audits (url, score, metrics_json, report_json, created_at) VALUES (?, ?, ?, ?, ?)",
        (url, score, json.dumps(metrics), json.dumps(report), int(time.time()))
    )
    conn.commit()
    conn.close()

def get_seo_audits() -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM seo_audits ORDER BY created_at DESC").fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res

def save_keyword_report(topic: str, results: Dict):
    conn = get_connection()
    conn.execute(
        "INSERT INTO keyword_reports (topic, results_json, created_at) VALUES (?, ?, ?)",
        (topic, json.dumps(results), int(time.time()))
    )
    conn.commit()
    conn.close()

def get_keyword_reports() -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM keyword_reports ORDER BY created_at DESC").fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res
def get_total_leads_count() -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM leads")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_campaigns() -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res

def get_campaign_leads_count(campaign_id: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM leads WHERE campaign_id = ?", (campaign_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def create_campaign(data: Dict[str, Any]):
    conn = get_connection()
    keys = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    conn.execute(f"INSERT INTO campaigns ({keys}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    conn.close()

def get_leads_paginated(page: int, page_size: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    offset = (page - 1) * page_size
    rows = conn.execute("SELECT * FROM leads ORDER BY id DESC LIMIT ? OFFSET ?", (page_size, offset)).fetchall()
    res = [dict(r) for r in rows]
    conn.close()
    return res

def delete_leads(lead_ids: List[int]):
    conn = get_connection()
    placeholders = ", ".join(["?" for _ in lead_ids])
    conn.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", lead_ids)
    conn.commit()
    conn.close()

def get_pipeline_stats() -> Dict[str, Any]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    stocks = ["new", "qualified", "negotiation", "closed"]
    res = {}
    for s in stocks:
        row = conn.execute("SELECT count(*), sum(confidence) FROM leads WHERE status = ?", (s,)).fetchone()
        res[s] = {"count": row[0] or 0, "value": row[1] or 0}
    conn.close()
    return res

def get_dashboard_stats() -> Dict[str, Any]:
    conn = get_connection()
    total_leads = conn.execute("SELECT count(*) FROM leads").fetchone()[0]
    active_campaigns = conn.execute("SELECT count(*) FROM campaigns WHERE status = 'active'").fetchone()[0]
    # Simple success rate calculation
    total_closed = conn.execute("SELECT count(*) FROM leads WHERE status = 'closed'").fetchone()[0]
    success_rate = total_closed / total_leads if total_leads > 0 else 0
    conn.close()
    return {
        "total_leads": total_leads,
        "active_campaigns": active_campaigns,
        "success_rate": success_rate
    }
