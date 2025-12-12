import re
import datetime
import os

TASK_FILE = r'C:\Users\baron\.gemini\antigravity\brain\7597ec01-058a-4544-9272-9aef51e2f284\task.md'
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
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg: #111;
            --card-bg: #1a1a1a;
            --text: #eee;
            --text-muted: #aaa;
            --accent: #d4af37; /* Gold */
            --accent-dim: #8a7020;
            --success: #4caf50;
            --progress-bg: #333;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 50px;
            border-bottom: 1px solid #333;
            padding-bottom: 30px;
        }}
        h1 {{
            font-weight: 300;
            letter-spacing: -1px;
            margin: 0 0 10px 0;
            font-size: 2.5rem;
        }}
        .meta {{
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .global-progress {{
            background: var(--card-bg);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid #333;
        }}
        .stat-box h3 {{ margin: 0; font-size: 3rem; color: var(--accent); font-weight: 300; }}
        .stat-box p {{ margin: 0; color: var(--text-muted); text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; }}
        
        .phase-card {{
            background: var(--card-bg);
            border-radius: 8px;
            margin-bottom: 30px;
            overflow: hidden;
            border: 1px solid #333;
        }}
        .phase-header {{
            padding: 20px 30px;
            background: #222;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}
        .phase-header h2 {{ margin: 0; font-size: 1.2rem; font-weight: 500; }}
        .phase-meta {{ color: var(--text-muted); font-size: 0.9rem; }}
        
        .progress-bar-container {{
            height: 4px;
            background: var(--progress-bg);
            width: 100%;
        }}
        .progress-bar-fill {{
            height: 100%;
            background: var(--accent);
            transition: width 0.3s ease;
        }}
        
        .task-list {{
            padding: 20px 30px;
        }}
        .task-item {{
            padding: 8px 0;
            display: flex;
            align-items: flex-start;
            border-bottom: 1px solid #2a2a2a;
        }}
        .task-item:last-child {{ border-bottom: none; }}
        .status-icon {{
            margin-right: 15px;
            font-size: 1.1rem;
            width: 20px;
            text-align: center;
        }}
        .status-done {{ color: var(--success); }}
        .status-inprogress {{ color: var(--accent); }}
        .status-todo {{ color: #444; }}
        
        .task-text {{ font-size: 0.95rem; }}
        .task-done .task-text {{ color: var(--text-muted); text-decoration: line-through; opacity: 0.6; }}
        
        @media (max-width: 600px) {{
            .global-progress {{ flex-direction: column; text-align: center; gap: 20px; }}
            h1 {{ font-size: 1.8rem; }}
        }}
    </style>
</head>
<body>
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
</body>
</html>
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
