import sqlite3
import time
import json
from .base import get_connection
from utils.db_writer import get_db_writer

def save_influencer_candidate(data):
    """Saves a single influencer candidate."""
    conn = get_connection()
    c = conn.cursor()
    try:
        handle = data.get('handle')
        platform = data.get('platform')
        url = data.get('url')
        niche = data.get('niche')
        try:
             follower_count = int(data.get('expected_followers') or data.get('estimated_followers') or 0)
        except:
             follower_count = 0
             
        bio = data.get('bio_snippet') or data.get('description', '')
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
    count = 0
    try:
        for data in candidates:
            handle = data.get('handle')
            url = data.get('url')
            if not url: continue
            platform = data.get('platform', 'unknown')
            niche = data.get('niche', '')
            try:
                follower_count = int(data.get('estimated_followers', 0))
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

def get_influencer_candidates(limit=50, status=None, niche=None, platform=None, offset=0):
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
    c.execute(query, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def update_influencer_status(candidate_id, new_status):
    """Updates the status of a candidate."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE influencer_candidates SET status=? WHERE id=?", (new_status, candidate_id))
    conn.commit()
    conn.close()

def delete_influencer_candidates(candidate_ids):
    """Deletes candidates by a list of IDs."""
    if not candidate_ids: return False
    conn = get_connection()
    c = conn.cursor()
    placeholders = ','.join('?' * len(candidate_ids))
    c.execute(f"DELETE FROM influencer_candidates WHERE id IN ({placeholders})", candidate_ids)
    conn.commit()
    conn.close()
    return True

def get_influencer_stats():
    """Returns counts of candidates grouped by status."""
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT status, COUNT(*) FROM influencer_candidates GROUP BY status")
    for row in c.fetchall():
        stats[row[0]] = row[1]
    conn.close()
    return stats
