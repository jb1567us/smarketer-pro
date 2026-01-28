import sqlite3
import time
from .base import get_connection
from utils.db_writer import get_db_writer

# Simple TTL cache for proxy queries
_proxy_cache = {}
_cache_ttl = 30  # seconds

def _get_from_cache(key):
    if key in _proxy_cache:
        value, timestamp = _proxy_cache[key]
        if time.time() - timestamp < _cache_ttl:
            return value
        else:
            del _proxy_cache[key]
    return None

def _set_cache(key, value):
    _proxy_cache[key] = (value, time.time())

def invalidate_proxy_cache():
    """Invalidate all proxy caches. Call after proxy pool updates."""
    global _proxy_cache
    _proxy_cache = {}

def save_proxies(proxy_list, reset=False):
    """Saves or updates a list of proxies."""
    writer = get_db_writer()
    now = int(time.time())

    if reset:
        writer.execute_write('DELETE FROM proxies', wait=True)

    query = '''
            INSERT INTO proxies (address, protocol, anonymity, country, latency, last_checked_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(address) DO UPDATE SET
                protocol=COALESCE(excluded.protocol, protocol),
                anonymity=excluded.anonymity,
                country=COALESCE(excluded.country, country),
                latency=excluded.latency,
                last_checked_at=excluded.last_checked_at,
                is_active=1
        '''
    
    params_list = []
    for p in proxy_list:
        params_list.append((
            p['address'], 
            p.get('protocol', 'http'), 
            p.get('anonymity', 'standard'), 
            p.get('country', 'Unknown'),
            p.get('latency', 0),
            now,
            now
        ))
        
    if params_list:
        writer.execute_many_write(query, params_list, wait=True)
        invalidate_proxy_cache()  # Invalidate cache after updates

def get_best_proxies(limit=50, min_anonymity=None, min_success_count=0):
    """
    Retrieves proxies ordered by success rate and latency.
    Results are cached for 30 seconds to improve performance.
    """
    # Check cache first
    cache_key = f"best_proxies_{limit}_{min_anonymity}_{min_success_count}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached
    
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        query = 'SELECT * FROM proxies WHERE is_active = 1'
        params = []
        if min_anonymity:
            query += ' AND anonymity = ?'
            params.append(min_anonymity)
            
        if min_success_count > 0:
            query += ' AND success_count >= ?'
            params.append(min_success_count)
        
        query += ' ORDER BY (CAST(success_count AS REAL) / (success_count + fail_count + 1)) DESC, latency ASC LIMIT ?'
        params.append(limit)
        
        c.execute(query, params)
        results = [dict(r) for r in c.fetchall()]
        
        # Store in cache
        _set_cache(cache_key, results)
        return results
    except Exception as e:
        print(f"DB Error getting best proxies: {e}")
        return []
    finally:
        conn.close()

def update_proxy_health(address, success=True, latency=None):
    """Updates proxy stats after a check or use."""
    writer = get_db_writer()
    now = int(time.time())
    
    if success:
        query = '''
            UPDATE proxies 
            SET success_count = success_count + 1, 
                fail_count = 0,
                last_used_at = ?, 
                last_checked_at = ?,
                latency = COALESCE(?, latency),
                is_active = 1
            WHERE address = ?
        '''
        params = (now, now, latency, address)
    else:
        query = '''
            UPDATE proxies 
            SET fail_count = fail_count + 1, 
                last_checked_at = ?,
                is_active = CASE WHEN fail_count > 10 THEN 0 ELSE 1 END
            WHERE address = ?
        '''
        params = (now, address)
        
    writer.execute_write(query, params, wait=False)

def update_proxy_source_status(url, success=True, content_hash=None, yield_count=0):
    """Updates proxy source metadata."""
    writer = get_db_writer()
    now = int(time.time())
    
    if success:
        query = '''
            UPDATE proxy_sources 
            SET last_checked = ?, 
                success_count = success_count + 1,
                consecutive_failures = 0,
                content_hash = COALESCE(?, content_hash)
            WHERE url = ?
        '''
        params = (now, content_hash, url)
    else:
        query = '''
            UPDATE proxy_sources 
            SET last_checked = ?, 
                fail_count = fail_count + 1,
                consecutive_failures = consecutive_failures + 1,
                is_active = CASE WHEN consecutive_failures > 5 THEN 0 ELSE 1 END
            WHERE url = ?
        '''
        params = (now, url)
        
    writer.execute_write(query, params, wait=False)

def clear_proxies():
    """Wipes the proxy table."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM proxies')
    conn.commit()
    conn.close()

def get_proxy_sources(active_only=True):
    """Retrieves all registered proxy sources."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        query = "SELECT * FROM proxy_sources"
        if active_only:
            query += " WHERE is_active = 1"
        c.execute(query)
        return [dict(r) for r in c.fetchall()]
    except Exception as e:
        print(f"DB Error getting proxy sources: {e}")
        return []
    finally:
        conn.close()

def add_proxy_source(url, category="public"):
    """Adds a new proxy source URL to the system."""
    writer = get_db_writer()
    now = int(time.time())
    query = '''
        INSERT INTO proxy_sources (url, category, created_at, last_checked)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO NOTHING
    '''
    writer.execute_write(query, (url, category, now, 0), wait=True)
