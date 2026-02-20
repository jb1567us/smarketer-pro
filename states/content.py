import reflex as rx
import asyncio
import time
import json
from typing import List, Dict, Any, Optional
from .base import BaseState
from backend.database import get_connection
from backend.agents.visual_agent import visual_agent

class ContentState(BaseState):
    """Reflex state for Phase 9: Outreach Optimizer (Visual Studio)."""
    
    asset_gallery: List[Dict[str, Any]] = []
    is_designing: bool = False
    
    async def poll_content_assets(self):
        """Update content asset gallery from DB."""
        while True:
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute('''
                    SELECT id, lead_id, asset_type, layout_json, status, timestamp 
                    FROM content_assets 
                    ORDER BY timestamp DESC LIMIT 5
                ''')
                results = c.fetchall()
                self.asset_gallery = [
                    {
                        "id": r[0],
                        "lead_id": r[1],
                        "type": r[2],
                        "layout": json.loads(r[3]),
                        "status": r[4],
                        "ts": r[5]
                    } for r in results
                ]
                conn.close()
            except Exception as e:
                print(f"Content polling error: {e}")
            
            await asyncio.sleep(8)

    async def create_carousel_for_lead(self, lead_data: Dict[str, Any]):
        """Design a new carousel for a specific prospect."""
        self.is_designing = True
        self.add_log(f"🎨 Visual Studio: Designing carousel for {lead_data.get('name')}...")
        yield
        
        try:
            # 1. Generate Layout
            layout = await visual_agent.generate_carousel_layout(lead_data)
            
            # 2. Persist to DB
            conn = get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO content_assets (lead_id, asset_type, layout_json, status, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (lead_data.get("id"), "carousel", json.dumps(layout), "final", int(time.time())))
            conn.commit()
            conn.close()
            
            self.add_log(f"✅ Visual Studio: Carousel Complete for {lead_data.get('name')}")
        except Exception as e:
            self.add_log(f"❌ Design Error: {e}")
            
        self.is_designing = False
        yield

    @rx.var
    def total_assets(self) -> int:
        return len(self.asset_gallery)
