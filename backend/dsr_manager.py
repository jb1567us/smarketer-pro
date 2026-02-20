import time
import json
from typing import List, Dict, Any
from .database import get_connection

class DSRManager:
    def __init__(self):
        pass

    async def generate_dsr_for_lead(self, campaign_id: int, lead_data: Dict):
        """Mock DSR generation logic."""
        # This would normally call an agent to generate copy/images
        content = {
            "copy": {
                "headline": f"Exclusive Solution for {lead_data.get('company_name', 'your company')}",
                "sub_headline": "Optimizing your outreach with AI-driven precision.",
                "benefits": ["Increased ROI", "Automated Lead Gen", "Premium Support"]
            },
            "hero_image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60"
        }
        
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO digital_sales_rooms (lead_id, campaign_id, title, content_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (lead_data.get('id'), campaign_id, f"DSR for {lead_data.get('company_name')}", json.dumps(content), int(time.time())))
        conn.commit()
        conn.close()
        
        return {"status": "success", "content": content}

    def get_all_dsrs(self) -> List[Dict]:
        conn = get_connection()
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        c = conn.cursor()
        c.execute('SELECT * FROM digital_sales_rooms ORDER BY created_at DESC')
        res = c.fetchall()
        conn.close()
        return res
