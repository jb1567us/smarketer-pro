import sqlite3
import time
import json
from .base import get_connection
from utils.db_writer import get_db_writer

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
    writer = get_db_writer()
    params_json = json.dumps(tool_params) if tool_params else None
    
    query = '''
        INSERT INTO chat_messages (session_id, role, content, tool_call, tool_params, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    params = (session_id, role, content, tool_call, params_json, int(time.time()))
    writer.execute_write(query, params, wait=False)

def get_chat_history(session_id):
    """Retrieves all messages for a specific session."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT role, content, tool_call, tool_params FROM chat_messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
    results = []
    for r in c.fetchall():
        d = dict(r)
        if d.get('tool_params'):
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

def delete_chat_session(session_id):
    """Deletes a chat session and its messages."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
    c.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
