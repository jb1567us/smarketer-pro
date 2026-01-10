import re
import os
from bs4 import BeautifulSoup

HTML_FILE = r'C:\sandbox\esm\client_dashboard.html'
OUTPUT_FILE = r'C:\sandbox\esm\PROJECT_STATUS.md'

def recover_tasks():
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} not found.")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    title_elem = soup.find('h1')
    title = title_elem.text.strip() if title_elem else "Project Status"

    markdown_content = f"# {title}\n\n"

    phases = soup.find_all('div', class_='phase-card')
    
    for phase in phases:
        header = phase.find('div', class_='phase-header')
        h2 = header.find('h2') if header else None
        phase_name = h2.text.strip() if h2 else "Unknown Phase"
        
        markdown_content += f"## {phase_name}\n\n"
        
        task_list = phase.find('div', class_='task-list')
        if task_list:
            items = task_list.find_all('div', class_='task-item')
            for item in items:
                text_div = item.find('div', class_='task-text')
                text = text_div.text.strip() if text_div else "Unknown Task"
                
                # Check status class
                classes = item.get('class', [])
                if 'task-done' in classes:
                    marker = '[x]'
                elif 'task-inprogress' in classes:
                    marker = '[/]'
                else:
                    marker = '[ ]'
                    
                markdown_content += f"- {marker} {text}\n"
        
        markdown_content += "\n"

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
        
    print(f"Successfully recovered tasks to {OUTPUT_FILE}")

if __name__ == "__main__":
    recover_tasks()
