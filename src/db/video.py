import sqlite3
import time
from .base import get_connection

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
    try:
        c.execute('SELECT * FROM video_history ORDER BY created_at DESC LIMIT ?', (limit,))
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

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
