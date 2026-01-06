import re
import datetime
import os

TASK_FILE = r'C:\sandbox\esm\PROJECT_STATUS.md'
OUTPUT_FILE = r'C:\sandbox\esm\client_dashboard.html'

def parse_task_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    phases = []
    current_phase = None
    title = "Project Status"

    for line in lines:
        line = line.strip()
        
        if line.startswith('# '):
            title = line[2:].strip()
            continue
            
        if line.startswith('## '):
            if current_phase:
                phases.append(current_phase)
            current_phase = {
                'name': line[3:].strip(),
                'tasks': [],
                'completed': 0,
                'total': 0
            }
            continue
            
        if line.startswith('- [') and current_phase:
            is_completed = line.startswith('- [x]')
            is_in_progress = line.startswith('- [/]')
            task_text = line[6:].strip()
            
            status = 'todo'
            if is_completed: status = 'done'
            elif is_in_progress: status = 'inprogress'
            
            current_phase['tasks'].append({
                'text': task_text,
                'status': status
            })
            current_phase['total'] += 1
            if is_completed:
                current_phase['completed'] += 1

    if current_phase:
        phases.append(current_phase)
        
    return title, phases

def generate_html(title, phases):
    # Calculate Global Stats
    total_tasks = sum(p['total'] for p in phases)
    total_completed = sum(p['completed'] for p in phases)
    global_progress = int((total_completed / total_tasks) * 100) if total_tasks > 0 else 0
    
    today = datetime.datetime.now().strftime("%B %d, %Y")
    html = f"""
    <div class="container">
        <header>
            <div class="meta">Project Implementation Status</div>
            <h1>{title}</h1>
            <div class="meta" style="color: var(--text-muted); margin-top: 10px;">Last Updated: {today}</div>
        </header>
        
        <div class="global-progress">
            <div class="stat-box">
                <h3>{global_progress}%</h3>
                <p>Overall Completion</p>
            </div>
            <div class="stat-box">
                <h3>{total_completed} <span style="font-size:1.5rem; color:#555;">/ {total_tasks}</span></h3>
                <p>Tasks Completed</p>
            </div>
        </div>
        
    """
    
    for p in phases:
        percent = int((p['completed'] / p['total']) * 100) if p['total'] > 0 else 0
        html += f"""
        <div class="phase-card">
            <div class="phase-header">
                <h2>{p['name']}</h2>
                <div class="phase-meta">{p['completed']}/{p['total']} Tasks ({percent}%)</div>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: {percent}%"></div>
            </div>
            <div class="task-list">
        """
        
        for task in p['tasks']:
            icon = "○"
            status_class = "status-todo"
            row_class = "task-todo"
            
            if task['status'] == 'done':
                icon = "●" # or ✓
                status_class = "status-done"
                row_class = "task-done"
            elif task['status'] == 'inprogress':
                icon = "◑"
                status_class = "status-inprogress"
                row_class = "task-inprogress"
                
            html += f"""
                <div class="task-item {row_class}">
                    <div class="status-icon {status_class}">{icon}</div>
                    <div class="task-text">{task['text']}</div>
                </div>
            """
            
        html += """
            </div>
        </div>
        """
        
    html += """
    </div>
    """
    return html

# EXECUTION
try:
    title, phases = parse_task_md(TASK_FILE)
    html_content = generate_html(title, phases)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Successfully generated dashboard at: {OUTPUT_FILE}")
    print(f"Title: {title}")
    print(f"Phases found: {len(phases)}")
    
except Exception as e:
    print(f"Error: {e}")
