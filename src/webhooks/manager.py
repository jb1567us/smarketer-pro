"""
Webhook system for event-driven automation.
"""
import requests
import json
import hashlib
import hmac
from typing import Dict, List, Any
from datetime import datetime
import sqlite3
from database import get_connection

class WebhookManager:
    """Manages webhook registrations and deliveries."""
    
    def __init__(self):
        self._init_database()
    
    def _init_database(self):
        """Initialize webhook storage tables."""
        conn = get_connection()
        c = conn.cursor()
        
        try:
            # Webhooks table
            c.execute('''
                CREATE TABLE IF NOT EXISTS webhooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    events TEXT NOT NULL,
                    secret TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Webhook deliveries table
            c.execute('''
                CREATE TABLE IF NOT EXISTS webhook_deliveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    webhook_id INTEGER,
                    event_type TEXT,
                    payload TEXT,
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    last_attempt TIMESTAMP,
                    response_code INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
                )
            ''')
            
            conn.commit()
        finally:
            conn.close()
    
    def register_webhook(self, url: str, events: List[str], secret: str = None) -> int:
        """Register a new webhook."""
        conn = get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO webhooks (url, events, secret)
                VALUES (?, ?, ?)
            ''', (url, json.dumps(events), secret))
            
            conn.commit()
            return c.lastrowid
        finally:
            conn.close()
    
    def get_webhooks(self, event_type: str = None) -> List[Dict]:
        """Get  all active webhooks, optionally filtered by event type."""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM webhooks WHERE is_active = 1")
            webhooks = [dict(row) for row in c.fetchall()]
            
            if event_type:
                # Filter by event type
                filtered = []
                for wh in webhooks:
                    events = json.loads(wh['events'])
                    if event_type in events or '*' in events:
                        filtered.append(wh)
                return filtered
            
            return webhooks
        finally:
            conn.close()
    
    def deactivate_webhook(self, webhook_id: int):
        """Deactivate a webhook."""
        conn = get_connection()
        c = conn.cursor()
        
        try:
            c.execute("UPDATE webhooks SET is_active = 0 WHERE id = ?", (webhook_id,))
            conn.commit()
        finally:
            conn.close()
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def deliver_webhook(self, webhook_id: int, event_type: str, payload: Dict) -> bool:
        """Deliver a webhook with retry logic."""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            # Get webhook details
            c.execute("SELECT * FROM webhooks WHERE id = ? AND is_active = 1", (webhook_id,))
            webhook = c.fetchone()
            
            if not webhook:
                return False
            
            webhook = dict(webhook)
            payload_json = json.dumps(payload)
            
            # Create delivery record
            c.execute('''
                INSERT INTO webhook_deliveries (webhook_id, event_type, payload)
                VALUES (?, ?, ?)
            ''', (webhook_id, event_type, payload_json))
            delivery_id = c.lastrowid
            conn.commit()
            
            # Prepare headers
            headers = {'Content-Type': 'application/json'}
            
            # Add signature if secret is set
            if webhook['secret']:
                signature = self._generate_signature(payload_json, webhook['secret'])
                headers['X-Webhook-Signature'] = signature
            
            # Attempt delivery with retries
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    response = requests.post(
                        webhook['url'],
                        json=payload,
                        headers=headers,
                        timeout=10
                    )
                    
                    # Update delivery status
                    c.execute('''
                        UPDATE webhook_deliveries 
                        SET status = ?, attempts = ?, last_attempt = ?, response_code = ?
                        WHERE id = ?
                    ''', (
                        'success' if response.status_code < 400 else 'failed',
                        attempt,
                        datetime.now().isoformat(),
                        response.status_code,
                        delivery_id
                    ))
                    conn.commit()
                    
                    if response.status_code < 400:
                        return True
                
                except Exception as e:
                    # Log failed attempt
                    c.execute('''
                        UPDATE webhook_deliveries 
                        SET status = 'failed', attempts = ?, last_attempt = ?
                        WHERE id = ?
                    ''', (attempt, datetime.now().isoformat(), delivery_id))
                    conn.commit()
                    
                    if attempt == max_attempts:
                        return False
            
            return False
        
        finally:
            conn.close()
    
    def trigger_event(self, event_type: str, payload: Dict):
        """Trigger an event and deliver to all subscribed webhooks."""
        webhooks = self.get_webhooks(event_type)
        
        for webhook in webhooks:
            self.deliver_webhook(webhook['id'], event_type, payload)

# Event types
EVENTS = {
    'lead.created': 'Triggered when a new lead is created',
    'lead.updated': 'Triggered when a lead is updated',
    'lead.enriched': 'Triggered when a lead is enriched',
    'campaign.created': 'Triggered when a campaign is created',
    'campaign.completed': 'Triggered when a campaign completes'
}
