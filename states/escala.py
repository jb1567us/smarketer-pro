import reflex as rx
import asyncio
import time
import json
from typing import List, Dict, Any, Optional
from .base import BaseState
from backend.database import get_connection

class EscalaState(BaseState):
    """Reflex state for Phase 8: Escala Protocol (HITL)."""
    
    escalation_queue: List[Dict[str, Any]] = []
    has_pending: bool = False
    
    async def poll_escalations(self):
        """Monitor for pending high-risk approval requests."""
        while True:
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute('''
                    SELECT id, operation_type, risk_level, context_json, status, timestamp 
                    FROM escalations 
                    WHERE status = 'pending' 
                    ORDER BY timestamp DESC
                ''')
                results = c.fetchall()
                self.escalation_queue = [
                    {
                        "id": r[0],
                        "type": r[1],
                        "level": r[2],
                        "context": json.loads(r[3]),
                        "status": r[4],
                        "ts": r[5]
                    } for r in results
                ]
                self.has_pending = len(self.escalation_queue) > 0
                conn.close()
            except Exception as e:
                print(f"Escala polling error: {e}")
            
            await asyncio.sleep(5)

    async def sign_off_request(self, request_id: int, decision: str):
        """Manual Approve or Reject action."""
        status = "approved" if decision == "allow" else "rejected"
        self.add_log(f"🛡️ Escala: Risk Sign-off ({status}) for ID {request_id}")
        
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "UPDATE escalations SET status = ?, approved_by = ? WHERE id = ?",
                (status, "admin", request_id)
            )
            conn.commit()
            conn.close()
            
            # Instant refresh of the queue
            self.escalation_queue = [e for e in self.escalation_queue if e["id"] != request_id]
            self.has_pending = len(self.escalation_queue) > 0
        except Exception as e:
            self.add_log(f"❌ Escala Update Error: {e}")
        
        yield

    @rx.var
    def pending_count(self) -> int:
        return len(self.escalation_queue)
