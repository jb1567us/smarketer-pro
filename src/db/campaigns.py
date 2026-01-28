import sqlite3
import time
import json
from .base import get_connection, get_current_workspace_id
from utils.db_writer import get_db_writer

# --- CAMPAIGNS ---
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

def get_campaign(campaign_id):
    """Retrieves full campaign data."""
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
    c.execute('DELETE FROM campaign_leads WHERE campaign_id = ?', (campaign_id,))
    c.execute('DELETE FROM email_templates WHERE campaign_id = ?', (campaign_id,))
    c.execute('DELETE FROM campaigns WHERE id = ?', (campaign_id,))
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
    c.execute('UPDATE campaigns SET selected_pain_point_id = ?, updated_at = ? WHERE id = ?', (pain_point_id, int(time.time()), campaign_id))
    conn.commit()
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

# --- PAIN POINTS & TEMPLATES ---
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
    """Retrieves templates for a niche or campaign."""
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

# --- ANALYTICS & EVENTS ---
def log_campaign_event(email, event_type, template_id=None, event_data=None, lead_id=None, campaign_id=None):
    """Logs an event (sent, open, click) for a lead."""
    writer = get_db_writer()
    query = '''
        INSERT INTO campaign_events (lead_email, template_id, event_type, event_data, timestamp, lead_id, campaign_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    params = (email, template_id, event_type, event_data, int(time.time()), lead_id, campaign_id)
    writer.execute_write(query, params, wait=False)

def get_campaign_analytics():
    """Aggregates campaign events by type."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT event_type, COUNT(*) FROM campaign_events GROUP BY event_type')
    results = dict(c.fetchall())
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
    c.execute(f'''
        SELECT strftime('%Y-%m-%d', timestamp, 'unixepoch') as day, event_type, COUNT(*)
        FROM campaign_events
        WHERE timestamp > strftime('%s', 'now', '-{days} days')
        GROUP BY day, event_type
        ORDER BY day ASC
    ''')
    rows = c.fetchall()
    conn.close()
    data = {}
    for r in rows:
        day, etype, count = r
        if day not in data: data[day] = {'sent': 0, 'open': 0, 'click': 0}
        data[day][etype] = count
    return data

# --- LINK WHEELS ---
def save_link_wheel(money_site_url, strategy, plan_json):
    """Saves a generated Link Wheel plan."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO link_wheels (money_site_url, strategy, tier_plan_json, created_at) VALUES (?, ?, ?, ?)',
              (money_site_url, strategy, plan_json, int(time.time())))
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

# --- SEQUENCES & CADENCES ---
def create_sequence(campaign_id, name):
    """Creates a new outreach sequence."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO sequences (campaign_id, name, created_at) VALUES (?, ?, ?)', (campaign_id, name, int(time.time())))
    seq_id = c.lastrowid
    conn.commit()
    conn.close()
    return seq_id

def add_sequence_step(sequence_id, step_number, touch_type, delay_days, content_json):
    """Adds a step to a sequence."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO sequence_steps (sequence_id, step_number, touch_type, delay_days, content_json) VALUES (?, ?, ?, ?, ?)',
              (sequence_id, step_number, touch_type, delay_days, content_json))
    conn.commit()
    conn.close()

def enroll_lead_in_sequence(lead_id, sequence_id):
    """Enrolls a lead in a sequence."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM sequence_enrollments WHERE lead_id = ? AND sequence_id = ?', (lead_id, sequence_id))
    if not c.fetchone():
        c.execute('INSERT INTO sequence_enrollments (lead_id, sequence_id, next_scheduled_at, status) VALUES (?, ?, ?, ?)',
                  (lead_id, sequence_id, int(time.time()), 'active'))
        conn.commit()
    conn.close()

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

def get_due_enrollments():
    """Returns all enrollments that are due for a touch."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT se.*, l.email, l.contact_person, l.company_name, s.campaign_id
        FROM sequence_enrollments se
        JOIN leads l ON se.lead_id = l.id
        JOIN sequences s ON se.sequence_id = s.id
        WHERE se.status = 'active' AND se.next_scheduled_at <= ?
    ''', (int(time.time()),))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_sequence_steps(sequence_id):
    """Returns all steps for a sequence."""
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

# --- DIGITAL SALES ROOMS ---
def create_dsr(campaign_id, lead_id, title, content_json, status='draft', site_id=None):
    """Creates a new Digital Sales Room entry."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO digital_sales_rooms (campaign_id, lead_id, site_id, title, content_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (campaign_id, lead_id, site_id, title, content_json, status, int(time.time())))
    dsr_id = c.lastrowid
    conn.commit()
    conn.close()
    return dsr_id

def update_dsr_wp_info(dsr_id, wp_page_id, public_url, status='published'):
    """Updates DSR with WordPress deployment info."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE digital_sales_rooms SET wp_page_id = ?, public_url = ?, status = ? WHERE id = ?',
              (wp_page_id, public_url, status, dsr_id))
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
    if isinstance(content_json, dict):
        content_json = json.dumps(content_json)
    try:
        c.execute("UPDATE digital_sales_rooms SET content_json = ? WHERE id = ?", (content_json, dsr_id))
        conn.commit()
    finally:
        conn.close()
