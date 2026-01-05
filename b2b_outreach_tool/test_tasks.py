
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from database import init_db, create_task, get_tasks, update_task, add_lead

def test_task_system():
    print("Initializing DB...")
    init_db()
    
    # Add a dummy lead first
    lead_id = add_lead("http://example.com", "test_task@example.com", company_name="Test Co")
    if not lead_id:
        # If lead exists, just get it (simple hack for test)
        import sqlite3
        conn = sqlite3.connect("leads.db")
        c = conn.cursor()
        c.execute("SELECT id FROM leads WHERE email='test_task@example.com'")
        lead_id = c.fetchone()[0]
        conn.close()
    
    print(f"Lead ID: {lead_id}")
    
    # Create a task
    print("Creating task...")
    task_id = create_task(
        lead_id=lead_id, 
        description="Follow up test task", 
        due_date=int(time.time()) + 86400,
        priority="Urgent",
        task_type="Follow-up"
    )
    print(f"Task created with ID: {task_id}")
    
    # Get tasks
    tasks = get_tasks()
    my_task = next((t for t in tasks if t['id'] == task_id), None)
    
    if my_task:
        print(f"Retrieved task: {my_task['description']}, Priority: {my_task['priority']}, Type: {my_task['task_type']}")
        assert my_task['priority'] == "Urgent"
        assert my_task['task_type'] == "Follow-up"
    else:
        print("Failed to retrieve task.")
        return
    
    # Update task
    print("Updating task status...")
    update_task(task_id, status="completed")
    
    updated_tasks = get_tasks(status="completed")
    if any(t['id'] == task_id for t in updated_tasks):
        print("Task update successful!")
    else:
        print("Task update failed.")

if __name__ == "__main__":
    import time
    test_task_system()
