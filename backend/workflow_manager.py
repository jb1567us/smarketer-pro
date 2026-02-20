import os
from typing import List, Optional

# Base directory for workflows as defined in the SystemState logic
WORKFLOW_DIR = r"C:\sandbox\b2b_outreach_proto\src\workflows"

def ensure_dir():
    if not os.path.exists(WORKFLOW_DIR):
        os.makedirs(WORKFLOW_DIR, exist_ok=True)

def list_workflows() -> List[str]:
    """List available workflow files in the workflows directory."""
    ensure_dir()
    try:
        return [f for f in os.listdir(WORKFLOW_DIR) if f.endswith('.md') or f.endswith('.json')]
    except Exception:
        return []

def read_workflow(name: str) -> Optional[str]:
    """Read the content of a specific workflow file."""
    ensure_dir()
    path = os.path.join(WORKFLOW_DIR, name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def save_workflow(name: str, content: str):
    """Save workflow content to a file."""
    ensure_dir()
    path = os.path.join(WORKFLOW_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def delete_workflow(name: str):
    """Delete a workflow file."""
    ensure_dir()
    path = os.path.join(WORKFLOW_DIR, name)
    if os.path.exists(path):
        os.remove(path)
