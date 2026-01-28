"""
Real-time progress tracking system using Server-Sent Events.
"""
import queue
import json
from datetime import datetime

class ProgressTracker:
    """Manages progress updates for long-running tasks."""
    
    def __init__(self):
        self.tasks = {}
        self.subscribers = {}
    
    def create_task(self, task_id: str, task_name: str, total_steps: int = 100):
        """Create a new task to track."""
        self.tasks[task_id] = {
            'id': task_id,
            'name': task_name,
            'total_steps': total_steps,
            'current_step': 0,
            'status': 'running',
            'message': 'Starting...',
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'progress_percent': 0
        }
        
        self._broadcast(task_id)
        return task_id
    
    def update_progress(self, task_id: str, current_step: int, message: str = None):
        """Update task progress."""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task['current_step'] = current_step
        task['progress_percent'] = int((current_step / task['total_steps']) * 100)
        
        if message:
            task['message'] = message
        
        self._broadcast(task_id)
    
    def complete_task(self, task_id: str, message: str = "Completed"):
        """Mark task as complete."""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task['status'] = 'completed'
        task['message'] = message
        task['progress_percent'] = 100
        task['completed_at'] = datetime.now().isoformat()
        
        self._broadcast(task_id)
    
    def fail_task(self, task_id: str, error: str):
        """Mark task as failed."""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task['status'] = 'failed'
        task['message'] = f"Error: {error}"
        task['completed_at'] = datetime.now().isoformat()
        
        self._broadcast(task_id)
    
    def get_task(self, task_id: str):
        """Get task status."""
        return self.tasks.get(task_id)
    
    def subscribe(self, task_id: str):
        """Subscribe to task updates (returns a queue)."""
        if task_id not in self.subscribers:
            self.subscribers[task_id] = []
        
        q = queue.Queue()
        self.subscribers[task_id].append(q)
        
        # Send current state immediately
        if task_id in self.tasks:
            q.put(json.dumps(self.tasks[task_id]))
        
        return q
    
    def _broadcast(self, task_id: str):
        """Broadcast update to all subscribers."""
        if task_id not in self.subscribers:
            return
        
        update = json.dumps(self.tasks[task_id])
        
        for q in self.subscribers[task_id]:
            try:
                q.put(update)
            except:
                pass

# Global progress tracker instance
progress_tracker = ProgressTracker()

# Flask SSE endpoint (to add to api/server.py)
def stream_progress(task_id):
    """SSE endpoint for streaming progress updates."""
    def generate():
        """Generate SSE events."""
        q = progress_tracker.subscribe(task_id)
        
        while True:
            try:
                update = q.get(timeout=30)
                yield f"data: {update}\n\n"
                
                # Check if task is done
                task = progress_tracker.get_task(task_id)
                if task and task['status'] in ['completed', 'failed']:
                    break
            except queue.Empty:
                # Send keep-alive
                yield ": keepalive\n\n"
    
    return generate()
