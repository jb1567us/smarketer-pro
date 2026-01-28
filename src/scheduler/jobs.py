"""
Job scheduling system for recurring tasks.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import sqlite3
from database import get_connection

class JobScheduler:
    """Manages scheduled and recurring jobs."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._init_database()
        self._load_jobs()
    
    def _init_database(self):
        """Initialize job storage table."""
        conn = get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    job_type TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    parameters TEXT,
                    is_active INTEGER DEFAULT 1,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    run_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def _load_jobs(self):
        """Load active jobs from database and schedule them."""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM scheduled_jobs WHERE is_active = 1")
            jobs = [dict(row) for row in c.fetchall()]
            
            for job in jobs:
                self._schedule_job(job)
        finally:
            conn.close()
    
    def _schedule_job(self, job_data: dict):
        """Schedule a job using APScheduler."""
        import json
        
        # Parse parameters
        params = json.loads(job_data.get('parameters', '{}'))
        
        # Create trigger based on schedule
        if job_data['job_type'] == 'cron':
            # Parse cron expression (e.g., "0 9 * * *" for daily at 9 AM)
            parts = job_data['schedule'].split()
            trigger = CronTrigger(
                minute=parts[0] if len(parts) > 0 else '*',
                hour=parts[1] if len(parts) > 1 else '*',
                day=parts[2] if len(parts) > 2 else '*',
                month=parts[3] if len(parts) > 3 else '*',
                day_of_week=parts[4] if len(parts) > 4 else '*'
            )
        elif job_data['job_type'] == 'interval':
            # Interval in minutes
            interval = int(job_data['schedule'])
            trigger = 'interval'
            params['minutes'] = interval
        
        # Add job to scheduler
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=trigger,
            args=[job_data['id'], job_data['function_name'], params],
            id=f"job_{job_data['id']}",
            name=job_data['name'],
            replace_existing=True
        )
    
    def _execute_job(self, job_id: int, function_name: str, parameters: dict):
        """Execute a scheduled job."""
        print(f"[JobScheduler] Executing job {job_id}: {function_name}")
        
        # Update job execution stats
        conn = get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                UPDATE scheduled_jobs 
                SET last_run = ?, run_count = run_count + 1
                WHERE id = ?
            ''', (datetime.now().isoformat(), job_id))
            conn.commit()
            
            # Execute the actual job function
            # This would map to actual functions in your codebase
            job_functions = {
                'daily_enrichment': self._daily_enrichment,
                'weekly_report': self._weekly_report,
                'proxy_health_check': self._proxy_health_check
            }
            
            if function_name in job_functions:
                job_functions[function_name](**parameters)
            else:
                print(f"[JobScheduler] Unknown function: {function_name}")
        
        except Exception as e:
            print(f"[JobScheduler] Error executing job {job_id}: {e}")
        finally:
            conn.close()
    
    def add_job(self, name: str, job_type: str, schedule: str, 
                function_name: str, parameters: dict = None) -> int:
        """Add a new scheduled job."""
        import json
        
        conn = get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO scheduled_jobs (name, job_type, schedule, function_name, parameters)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, job_type, schedule, function_name, json.dumps(parameters or {})))
            
            job_id = c.lastrowid
            conn.commit()
            
            # Schedule the job
            c.execute("SELECT * FROM scheduled_jobs WHERE id = ?", (job_id,))
            job_data = dict(c.fetchone())
            self._schedule_job(job_data)
            
            return job_id
        finally:
            conn.close()
    
    def remove_job(self, job_id: int):
        """Remove a scheduled job."""
        conn = get_connection()
        c = conn.cursor()
        
        try:
            c.execute("UPDATE scheduled_jobs SET is_active = 0 WHERE id = ?", (job_id,))
            conn.commit()
            
            # Remove from scheduler
            self.scheduler.remove_job(f"job_{job_id}")
        finally:
            conn.close()
    
    def get_jobs(self) -> list:
        """Get all scheduled jobs."""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM scheduled_jobs ORDER BY created_at DESC")
            return [dict(row) for row in c.fetchall()]
        finally:
            conn.close()
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            print("[JobScheduler] Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[JobScheduler] Scheduler stopped")
    
    # Example job functions
    def _daily_enrichment(self, **kwargs):
        """Run daily enrichment on leads."""
        print("[Job] Running daily enrichment...")
        # Implementation would go here
    
    def _weekly_report(self, **kwargs):
        """Generate weekly report."""
        print("[Job] Generating weekly report...")
        # Implementation would go here
    
    def _proxy_health_check(self, **kwargs):
        """Check proxy health."""
        print("[Job] Checking proxy health...")
        # Implementation would go here
