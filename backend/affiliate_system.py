import time
import json
import logging
from typing import List, Dict, Optional
from .database import get_connection

logger = logging.getLogger(__name__)

class AffiliateManager:
    def __init__(self):
        pass

    # My Links (Publisher)
    def add_my_program(self, program_name: str, login_url: str, username: str, dashboard_url: str, notes: str = "") -> int:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO my_affiliate_programs (program_name, login_url, username, dashboard_url, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (program_name, login_url, username, dashboard_url, notes, int(time.time())))
        pid = c.lastrowid
        conn.commit()
        conn.close()
        return pid

    def get_my_programs(self) -> List[Dict]:
        conn = get_connection()
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        c = conn.cursor()
        c.execute('SELECT * FROM my_affiliate_programs ORDER BY program_name ASC')
        res = c.fetchall()
        conn.close()
        return res

    def get_my_links(self) -> List[Dict]:
        conn = get_connection()
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        c = conn.cursor()
        c.execute('''
            SELECT l.*, p.program_name 
            FROM my_affiliate_links l
            LEFT JOIN my_affiliate_programs p ON l.program_id = p.id
            ORDER BY l.created_at DESC
        ''')
        res = c.fetchall()
        conn.close()
        return res

    # Brand Mode (Partners)
    def get_partners(self) -> List[Dict]:
        conn = get_connection()
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        c = conn.cursor()
        c.execute('SELECT * FROM partners ORDER BY created_at DESC')
        res = c.fetchall()
        conn.close()
        return res

    def get_partner_stats(self, partner_id: int) -> Dict:
        conn = get_connection()
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*), SUM(event_value), SUM(commission_generated) FROM partner_events WHERE partner_id = ? AND event_type = "sale"', (partner_id,))
        sales_data = c.fetchone()
        
        c.execute('SELECT COUNT(*) FROM partner_events WHERE partner_id = ? AND event_type = "click"', (partner_id,))
        clicks = c.fetchone()[0]
        conn.close()
        
        return {
            "clicks": clicks,
            "sales_count": sales_data[0] if sales_data[0] else 0,
            "total_revenue": sales_data[1] if sales_data[1] else 0.0,
            "commissions_earned": sales_data[2] if sales_data[2] else 0.0
        }
