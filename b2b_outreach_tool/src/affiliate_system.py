import logging
import time
import json
import random
from typing import List, Dict, Optional
from datetime import datetime
from database import get_connection

logger = logging.getLogger(__name__)

class AffiliateManager:
    """
    Handles both sides of the affiliate equation:
    1. Publisher Mode: Managing my own affiliate links (My Vault).
    2. Brand Mode: Managing partners who sell for me (Partner Center).
    """

    def __init__(self):
        self.conn = get_connection()

    # =========================================================================
    # PUBLISHER SIDE (My Links)
    # =========================================================================

    def add_my_program(self, program_name: str, login_url: str, username: str, dashboard_url: str, notes: str = "") -> int:
        """Adds a new affiliate program I belong to."""
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

    def add_my_link(self, program_id: int, target_url: str, cloaked_slug: str, category: str, commission_rate: str) -> int:
        """Adds a specific tracking link to a program."""
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO my_affiliate_links (program_id, target_url, cloaked_slug, category, commission_rate, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (program_id, target_url, cloaked_slug, category, commission_rate, int(time.time())))
        lid = c.lastrowid
        conn.commit()
        conn.close()
        return lid

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

    def check_link_health(self, link_id: int) -> Dict:
        """
        Real health check: Pings the target URL to see if it's 200 OK.
        Returns dict with status_code, is_alive, and response_time.
        """
        import requests
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT target_url FROM my_affiliate_links WHERE id = ?', (link_id,))
        res = c.fetchone()
        
        result = {"status_code": 0, "is_alive": False, "error": None}
        
        if res:
            url = res[0]
            try:
                start = time.time()
                resp = requests.head(url, timeout=5, allow_redirects=True)
                # If 405 Method Not Allowed (some servers block HEAD), try GET
                if resp.status_code == 405:
                    resp = requests.get(url, timeout=5, stream=True)
                
                result["status_code"] = resp.status_code
                result["is_alive"] = 200 <= resp.status_code < 400
                result["response_time"] = round(time.time() - start, 2)
                
                # Update DB
                status_str = "active" if result["is_alive"] else "broken"
                c.execute('UPDATE my_affiliate_links SET status = ?, last_checked_at = ? WHERE id = ?', 
                          (status_str, int(time.time()), link_id))
                conn.commit()
                
            except Exception as e:
                result["error"] = str(e)
                c.execute('UPDATE my_affiliate_links SET status = ?, last_checked_at = ? WHERE id = ?', 
                          ("broken", int(time.time()), link_id))
                conn.commit()
        
        conn.close()
        return result

    def record_click_on_my_link(self, link_id: int):
        """Simulates recording a click on one of my cloaked links."""
        conn = get_connection()
        c = conn.cursor()
        c.execute('UPDATE my_affiliate_links SET click_count = click_count + 1 WHERE id = ?', (link_id,))
        conn.commit()
        conn.close()

    # =========================================================================
    # BRAND SIDE (My Partners)
    # =========================================================================

    def add_partner(self, name: str, email: str, website: str, social_channels: Dict = None, payment_info: str = "") -> int:
        """Onboards a new partner."""
        conn = get_connection()
        c = conn.cursor()
        social_json = json.dumps(social_channels) if social_channels else "{}"
        try:
            c.execute('''
                INSERT INTO partners (name, email, website, social_channels_json, payment_info, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, website, social_json, payment_info, int(time.time())))
            pid = c.lastrowid
            conn.commit()
            return pid
        except Exception as e:
            logger.error(f"Error adding partner: {e}")
            return None
        finally:
            conn.close()

    def create_contract(self, partner_id: int, contract_type: str, terms: str, end_date: int = None) -> int:
        """Creates a commission agreement (e.g. 20% RevShare)."""
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO partner_contracts (partner_id, contract_type, terms, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (partner_id, contract_type, terms, int(time.time()), end_date))
        cid = c.lastrowid
        conn.commit()
        conn.close()
        return cid

    def log_partner_event(self, partner_id: int, event_type: str, event_value: float, source_url: str = ""):
        """
        Logs a sale or click. Automatically calculates commission based on active contract.
        """
        conn = get_connection()
        c = conn.cursor()
        
        # 1. Get active contract
        c.execute('''
            SELECT * FROM partner_contracts 
            WHERE partner_id = ? AND status = 'active' 
            ORDER BY id DESC LIMIT 1
        ''', (partner_id,))
        # Use row factory temporarily or just index
        contract = c.fetchone() # (id, pid, type, terms, start, end, status)
        
        commission = 0.0
        if contract and event_type == 'sale':
            c_type = contract[2]
            c_terms = contract[3]
            try:
                if c_type == 'RevShare':
                    # terms e.g. "20"
                    percentage = float(c_terms) / 100.0
                    commission = event_value * percentage
                elif c_type == 'CPA':
                    # terms e.g. "50"
                    commission = float(c_terms)
            except ValueError:
                logger.error(f"Invalid contract terms for partner {partner_id}")

        # 2. Log event
        c.execute('''
            INSERT INTO partner_events (partner_id, event_type, event_value, source_url, timestamp, commission_generated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (partner_id, event_type, event_value, source_url, int(time.time()), commission))
        
        conn.commit()
        conn.close()
        return commission

    def get_partners(self) -> List[Dict]:
        conn = get_connection()
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        c = conn.cursor()
        c.execute('SELECT * FROM partners ORDER BY created_at DESC')
        res = c.fetchall()
        conn.close()
        return res

    def get_partner_stats(self, partner_id: int) -> Dict:
        """Returns stats for a specific partner."""
        conn = get_connection()
        c = conn.cursor()
        
        # Total Sales
        c.execute('''
            SELECT COUNT(*), SUM(event_value), SUM(commission_generated) 
            FROM partner_events 
            WHERE partner_id = ? AND event_type = 'sale'
        ''', (partner_id,))
        sales_data = c.fetchone()
        
        # Total Clicks
        c.execute('''
            SELECT COUNT(*) FROM partner_events 
            WHERE partner_id = ? AND event_type = 'click'
        ''', (partner_id,))
        clicks = c.fetchone()[0]
        
        conn.close()
        
        return {
            "clicks": clicks,
            "sales_count": sales_data[0] if sales_data[0] else 0,
            "total_revenue": sales_data[1] if sales_data[1] else 0.0,
            "commissions_earned": sales_data[2] if sales_data[2] else 0.0
        }

    def generate_dummy_data(self):
        """Helper to seed DB for testing."""
        pid = self.add_partner("Jane Doe Streamer", "jane@twitch.tv", "twitch.tv/janedoe", {"twitch": "janedoe"}, "jane@paypal.com")
        if pid:
            self.create_contract(pid, "RevShare", "20")
            # Simulate some traffic
            for _ in range(5):
                self.log_partner_event(pid, "click", 0, "twitch.tv")
            # Simulate a sale
            self.log_partner_event(pid, "sale", 100.0, "twitch.tv")
