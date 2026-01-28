import sqlite3
import time
import json
from .base import get_connection, get_current_workspace_id
from utils.db_writer import get_db_writer

def add_lead(url, email, source="search", category="default", industry=None, business_type=None, confidence=None, relevance_reason=None, contact_person=None, company_name=None, address=None, phone_number=None, tech_stack=None, qualification_score=None, qualification_reason=None, workspace_id=None):
    """Adds a lead to the database. Returns ID if added, None if duplicate."""
    writer = get_db_writer()
    ws_id = get_current_workspace_id(workspace_id)
    
    query = '''
        INSERT INTO leads (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, created_at, workspace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    params = (url, email, source, category, industry, business_type, confidence, relevance_reason, contact_person, company_name, address, phone_number, tech_stack, qualification_score, qualification_reason, int(time.time()), ws_id)
    
    try:
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

def get_leads_by_status(status="new", workspace_id=None):
    """Retrieves all leads with a specific status, returning full details."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
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
    """Deletes ALL leads from the database."""
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
    placeholders = ','.join(['?'] * len(lead_ids))
    c.execute(f'DELETE FROM leads WHERE id IN ({placeholders})', lead_ids)
    conn.commit()
    conn.close()

def delete_lead(lead_id):
    """Deletes a single lead."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()

def update_lead(lead_id, data):
    """Updates a lead record with a dictionary of fields."""
    if not data: return
    conn = get_connection()
    c = conn.cursor()
    fields = [f"{k} = ?" for k in data.keys()]
    values = list(data.values()) + [lead_id]
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

def get_leads(limit=None, workspace_id=None):
    """Retrieves leads from the database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    if limit:
        c.execute("SELECT * FROM leads WHERE workspace_id = ? ORDER BY created_at DESC LIMIT ?", (ws_id, limit))
    else:
        c.execute("SELECT * FROM leads WHERE workspace_id = ? ORDER BY created_at DESC", (ws_id,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def save_agent_work_product(agent_role, input_task, output_content, tags=None, start_time=None, completion_time=None, metadata=None, artifact_type="text"):
    """Saves an agent's work product to the database."""
    writer = get_db_writer()
    tags_json = json.dumps(tags) if tags else "[]"
    meta_json = json.dumps(metadata) if metadata else "{}"
    
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

def log_agent_decision(agent_role, intent, user_input, tool_selected, tool_params, reasoning):
    """Logs an agent's reasoning and tool selection."""
    writer = get_db_writer()
    params_json = json.dumps(tool_params) if tool_params else "{}"
    query = '''
        INSERT INTO agent_decisions (agent_role, intent, user_input, tool_selected, tool_params, reasoning, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    params = (agent_role, intent, user_input, tool_selected, params_json, reasoning, int(time.time()))
    writer.execute_write(query, params, wait=False)
