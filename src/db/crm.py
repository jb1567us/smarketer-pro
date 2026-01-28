import sqlite3
import time
import json
from .base import get_connection, get_current_workspace_id
from utils.db_writer import get_db_writer

# --- DEALS ---
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
    c.execute('UPDATE deals SET stage = ?, probability = ? WHERE id = ?', (stage, probability, deal_id))
    conn.commit()
    conn.close()

def delete_deals_bulk(deal_ids):
    """Deletes multiple deals by their IDs."""
    if not deal_ids: return
    conn = get_connection()
    c = conn.cursor()
    placeholders = ','.join(['?'] * len(deal_ids))
    c.execute(f'DELETE FROM deals WHERE id IN ({placeholders})', deal_ids)
    conn.commit()
    conn.close()

# --- TASKS ---
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
    if not kwargs: return
    conn = get_connection()
    c = conn.cursor()
    fields = []
    params = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        params.append(value)
    params.append(task_id)
    c.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    conn.close()

def get_tasks(status=None, workspace_id=None):
    """Retrieves tasks, optionally filtered by status."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ws_id = get_current_workspace_id(workspace_id)
    query = 'SELECT t.*, l.company_name, l.contact_person FROM tasks t LEFT JOIN leads l ON t.lead_id = l.id WHERE t.workspace_id = ?'
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

def delete_task(task_id):
    """Deletes a task by ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# --- JUNCTION: CAMPAIGN LEADS ---
def add_lead_to_campaign(campaign_id, lead_id):
    """Links a lead to a campaign."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO campaign_leads (campaign_id, lead_id) VALUES (?, ?)', (campaign_id, lead_id))
        conn.commit()
    except sqlite3.IntegrityError: pass
    finally: conn.close()

def get_campaign_leads(campaign_id):
    """Retrieves all leads associated with a campaign."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT l.* FROM leads l JOIN campaign_leads cl ON l.id = cl.lead_id WHERE cl.campaign_id = ?', (campaign_id,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

# --- CREATIVE CONTENT LIBRARY ---
def save_creative_content(agent_type, content_type, title, body, metadata=None, workspace_id=None):
    """Saves generated creative content to the library."""
    conn = get_connection()
    c = conn.cursor()
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
