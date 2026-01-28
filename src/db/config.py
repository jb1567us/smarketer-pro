import sqlite3
import time
import json
from .base import get_connection
from config import config

def save_setting(key, value):
    """Saves a global application setting."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        ''', (key, str(value), int(time.time())))
        conn.commit()
    finally:
        conn.close()

def get_setting(key, default=None):
    """Retrieves a global application setting."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = c.fetchone()
        return result[0] if result else default
    finally:
        conn.close()

# --- PLATFORM CREDENTIALS ---
def save_platform_credential(platform_name, username=None, password=None, api_key=None, meta_json=None):
    """Saves or updates credentials for an external platform."""
    conn = get_connection()
    c = conn.cursor()
    try:
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
    finally:
        conn.close()

def get_platform_credentials(platform_name=None):
    """Retrieves credentials for one or all platforms."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        if platform_name:
            c.execute('SELECT * FROM platform_credentials WHERE platform_name = ?', (platform_name,))
            result = c.fetchone()
            return dict(result) if result else None
        else:
            c.execute('SELECT * FROM platform_credentials')
            return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def delete_platform_credential(platform_name):
    """Removes credentials for a platform."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM platform_credentials WHERE platform_name = ?', (platform_name,))
        conn.commit()
    finally:
        conn.close()

# --- CAPTCHA ---
def save_captcha_settings(provider, api_key, enabled):
    """Saves or updates captcha settings."""
    conn = get_connection()
    c = conn.cursor()
    try:
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
    finally:
        conn.close()

def get_captcha_settings():
    """Retrieves captcha settings, prioritizing config.yaml."""
    if config.get("captcha"):
        return config["captcha"]
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT provider, api_key, enabled FROM captcha_settings WHERE id = 1')
        row = c.fetchone()
        return dict(row) if row else {"provider": "none", "api_key": "", "enabled": 0}
    finally:
        conn.close()

# --- WP SITES ---
def save_wp_site(name, url, username, app_password, cp_url=None, cp_user=None, cp_pass=None):
    """Saves or updates a WordPress site's credentials."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT id FROM wp_sites WHERE name = ?', (name,))
        if c.fetchone():
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
    finally:
        conn.close()
    return True

def get_wp_sites():
    """Retrieves all saved WordPress sites."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM wp_sites ORDER BY name ASC')
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def delete_wp_site(site_id):
    """Deletes a saved WordPress site."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM wp_sites WHERE id = ?', (site_id,))
        conn.commit()
    finally:
        conn.close()

# --- CUSTOM AGENTS & PRESETS ---
def create_custom_agent(name, role, goal, system_prompt=None):
    """Creates a new custom agent."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO custom_agents (name, role, goal, system_prompt, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, role, goal, system_prompt, int(time.time())))
        agent_id = c.lastrowid
        conn.commit()
        return agent_id
    finally:
        conn.close()

def get_custom_agents():
    """Retrieves all custom agents."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM custom_agents ORDER BY name ASC')
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def delete_custom_agent(agent_id):
    """Deletes a custom agent."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM custom_agents WHERE id = ?', (agent_id,))
        conn.commit()
    finally:
        conn.close()

def save_strategy_preset(name, description, instruction_template, type="strategy"):
    """Saves a new strategy preset."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO strategy_presets (name, description, instruction_template, type, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, instruction_template, type, int(time.time())))
        preset_id = c.lastrowid
        conn.commit()
        return preset_id
    finally:
        conn.close()

def get_strategy_presets():
    """Retrieves all strategy presets."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM strategy_presets ORDER BY created_at DESC')
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def get_strategy_preset(preset_id):
    """Retrieves a single strategy preset."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM strategy_presets WHERE id = ?', (preset_id,))
        result = c.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()

def update_strategy_preset(preset_id, name, description, instruction_template):
    """Updates an existing strategy preset."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE strategy_presets 
            SET name = ?, description = ?, instruction_template = ?
            WHERE id = ?
        ''', (name, description, instruction_template, preset_id))
        conn.commit()
    finally:
        conn.close()

# --- SOCIAL ACCOUNTS & REGISTRATION ---
def save_managed_account(platform_name, email, username, password, proxy_used=None, metadata=None):
    """Saves a managed social account."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    try:
        c.execute('''
            INSERT INTO managed_accounts (platform_name, email, username, password, proxy_used, metadata, created_at, last_login_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (platform_name, email, username, password, proxy_used, json.dumps(metadata or {}), now, now))
        account_id = c.lastrowid
        conn.commit()
        return account_id
    finally:
        conn.close()

def get_managed_accounts(platform_name=None, status=None):
    """Retrieves managed accounts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        query = 'SELECT * FROM managed_accounts WHERE 1=1'
        params = []
        if platform_name:
            query += ' AND platform_name = ?'
            params.append(platform_name)
        if status:
            query += ' AND verification_status = ?'
            params.append(status)
        c.execute(query, params)
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def update_managed_account_status(account_id, status):
    """Updates the status of a managed account."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('UPDATE managed_accounts SET verification_status = ? WHERE id = ?', (status, account_id))
        conn.commit()
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
        c.execute("UPDATE managed_accounts SET platform_name = ?, username = ?, verification_status = ? WHERE id = ?", (platform, username, status, account_id))
        conn.commit()
    finally:
        conn.close()

def add_registration_task(platform, url, details=None):
    """Adds a registration task."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO registration_tasks (platform, url, details, created_at)
            VALUES (?, ?, ?, ?)
        ''', (platform, url, json.dumps(details or {}), int(time.time())))
        task_id = c.lastrowid
        conn.commit()
        return task_id
    finally:
        conn.close()

def get_registration_tasks(status='pending'):
    """Retrieves registration tasks."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM registration_tasks WHERE status = ? ORDER BY created_at DESC', (status,))
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def mark_registration_task_completed(task_id):
    """Marks a registration task as completed."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE registration_tasks SET status = 'completed' WHERE id = ?", (task_id,))
        conn.commit()
    finally:
        conn.close()

def save_registration_macro(platform, steps):
    """Saves or updates a registration macro for a platform."""
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    try:
        c.execute('''
            INSERT INTO registration_macros (platform, steps, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(platform) DO UPDATE SET
                steps=excluded.steps,
                updated_at=excluded.updated_at
        ''', (platform, json.dumps(steps), now, now))
        conn.commit()
    finally:
        conn.close()

def get_registration_macro(platform):
    """Retrieves a macro for a platform."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM registration_macros WHERE platform = ?', (platform,))
        result = c.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()
