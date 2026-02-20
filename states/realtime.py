"""
Real-time Event System

WebSocket-based real-time updates for:
- Campaign progress
- Lead enrichment status
- Agent operations
- System notifications
"""
import reflex as rx
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio


class RealtimeState(rx.State):
    """State for real-time updates"""
    
    # Notifications
    notifications: List[Dict[str, Any]] = []
    unread_count: int = 0
    
    # Progress tracking
    active_operations: Dict[str, Dict[str, Any]] = {}
    
    # Live stats
    live_campaign_count: int = 0
    live_lead_count: int = 0
    live_processing_count: int = 0
    
    # Connection status
    is_connected: bool = True
    last_update: str = ""
    
    def add_notification(
        self,
        title: str,
        message: str,
        type: str = "info",
        duration: int = 5000
    ):
        """Add a new notification"""
        notification = {
            "id": f"notif_{len(self.notifications)}",
            "title": title,
            "message": message,
            "type": type,  # info, success, warning, error
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "read": False
        }
        
        self.notifications.insert(0, notification)
        self.unread_count += 1
        
        # Keep only last 50
        if len(self.notifications) > 50:
            self.notifications = self.notifications[:50]
    
    def mark_notification_read(self, notif_id: str):
        """Mark notification as read"""
        for notif in self.notifications:
            if notif["id"] == notif_id and not notif["read"]:
                notif["read"] = True
                self.unread_count = max(0, self.unread_count - 1)
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        for notif in self.notifications:
            notif["read"] = True
        self.unread_count = 0
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications = []
        self.unread_count = 0
    
    def start_operation(
        self,
        operation_id: str,
        operation_type: str,
        total: int = 100
    ):
        """Start tracking an operation"""
        self.active_operations[operation_id] = {
            "type": operation_type,
            "progress": 0,
            "total": total,
            "status": "running",
            "started_at": datetime.now().isoformat()
        }
    
    def update_operation_progress(
        self,
        operation_id: str,
        progress: int,
        status: Optional[str] = None
    ):
        """Update operation progress"""
        if operation_id in self.active_operations:
            self.active_operations[operation_id]["progress"] = progress
            if status:
                self.active_operations[operation_id]["status"] = status
    
    def complete_operation(
        self,
        operation_id: str,
        success: bool = True
    ):
        """Mark operation as complete"""
        if operation_id in self.active_operations:
            op = self.active_operations[operation_id]
            op["status"] = "completed" if success else "failed"
            op["completed_at"] = datetime.now().isoformat()
            
            # Send notification
            if success:
                self.add_notification(
                    "Operation Complete",
                    f"{op['type']} finished successfully",
                    type="success"
                )
            else:
                self.add_notification(
                    "Operation Failed",
                    f"{op['type']} encountered an error",
                    type="error"
                )
            
            # Remove from active after delay (handled by frontend)
    
    def update_live_stats(self):
        """Update live dashboard stats"""
        from backend.database import Database
        
        db = Database()
        
        campaigns = db.get_all_campaigns()
        leads = db.get_all_leads()
        
        self.live_campaign_count = len(campaigns)
        self.live_lead_count = len(leads)
        
        # Count processing leads
        self.live_processing_count = sum(
            1 for lead in leads
            if lead.get("status") == "processing"
        )
        
        self.last_update = datetime.now().strftime("%H:%M:%S")
    
    async def auto_refresh_stats(self):
        """Auto-refresh stats every 5 seconds"""
        while True:
            self.update_live_stats()
            await asyncio.sleep(5)
    
    @rx.var
    def has_active_operations(self) -> bool:
        """Check if there are active operations"""
        return any(
            op["status"] == "running"
            for op in self.active_operations.values()
        )
    
    @rx.var
    def active_operation_count(self) -> int:
        """Count of active operations"""
        return sum(
            1 for op in self.active_operations.values()
            if op["status"] == "running"
        )


# Example usage functions for demonstration

def simulate_lead_enrichment(state: RealtimeState):
    """Simulate lead enrichment with progress updates"""
    import time
    
    operation_id = "enrich_001"
    total_leads = 50
    
    # Start operation
    state.start_operation(operation_id, "Lead Enrichment", total=total_leads)
    
    # Simulate progress
    for i in range(1, total_leads + 1):
        time.sleep(0.1)  # Simulate work
        state.update_operation_progress(
            operation_id,
            progress=i,
            status=f"Enriching lead {i}/{total_leads}"
        )
    
    # Complete
    state.complete_operation(operation_id, success=True)


def simulate_campaign_launch(state: RealtimeState):
    """Simulate campaign launch"""
    operation_id = "campaign_001"
    
    state.start_operation(operation_id, "Campaign Launch", total=100)
    
    # Stages
    stages = [
        (20, "Validating campaign..."),
        (40, "Preparing leads..."),
        (60, "Generating messages..."),
        (80, "Scheduling sends..."),
        (100, "Complete!")
    ]
    
    import time
    for progress, status in stages:
        time.sleep(0.5)
        state.update_operation_progress(operation_id, progress, status)
    
    state.complete_operation(operation_id, success=True)
