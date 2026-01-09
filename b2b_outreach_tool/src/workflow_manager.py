import os
import glob
import re
import json

WORKFLOW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent", "workflows")

def ensure_workflow_dir():
    """Ensures the workflow directory exists."""
    if not os.path.exists(WORKFLOW_DIR):
        os.makedirs(WORKFLOW_DIR)

def list_workflows():
    """Returns a list of available workflow files (basenames)."""
    ensure_workflow_dir()
    files = glob.glob(os.path.join(WORKFLOW_DIR, "*.md"))
    return [os.path.basename(f) for f in files]

def load_workflow(filename):
    """
    Reads a workflow file and returns metadata and content.
    Returns: dict(name, description, content)
    """
    path = os.path.join(WORKFLOW_DIR, filename)
    if not os.path.exists(path):
        return None
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract description from frontmatter if present
    description = ""
    match = re.search(r"^---\s+description:\s+(.+?)\s+---", content, re.DOTALL | re.MULTILINE)
    if match:
        description = match.group(1).strip()

    # Extract type from frontmatter
    wf_type = "workflow" # default
    match_type = re.search(r"^type:\s+(.+)$", content, re.MULTILINE)
    if match_type:
        wf_type = match_type.group(1).strip()
        
    return {
        "filename": filename,
        "description": description,
        "type": wf_type,
        "content": content
    }

def list_workflows(type_filter=None):
    """
    Returns a list of available workflow files (basenames).
    Optionally filters by type (e.g. 'strategy', 'task').
    """
    ensure_workflow_dir()
    files = glob.glob(os.path.join(WORKFLOW_DIR, "*.md"))
    
    if type_filter:
        filtered = []
        for f in files:
            # We need to peek at the content to check type without fully loading everything?
            # Or just load everything since there aren't many.
            try:
                data = load_workflow(os.path.basename(f))
                if data and data.get('type') == type_filter:
                    filtered.append(os.path.basename(f))
            except Exception:
                pass
        return filtered
            
    return [os.path.basename(f) for f in files]
def save_workflow(name, content, description="", steps=None, wf_type="workflow"):
    """
    Saves a workflow file.
    name: Filename (e.g. 'my_workflow.md') or simple name 'my_workflow'
    content: The markdown content (human readable)
    description: Short description for frontmatter
    steps: Optional list of dicts representing the executable steps
    wf_type: 'strategy' or 'task' (or 'workflow' default)
    """
    ensure_workflow_dir()
    
    if not name.endswith(".md"):
        name += ".md"
        
    # Sanitize filename
    name = re.sub(r"[^a-zA-Z0-9_\-\.]", "", name)
    
    # Serialize steps to JSON if provided
    steps_json = ""
    if steps:
        try:
            steps_json = json.dumps(steps, indent=2)
        except Exception as e:
            print(f"Error serializing steps: {e}")
            steps_json = "[]"

    # Construct content with frontmatter
    # We embed the steps in a special comment block or frontmatter field
    # Storing in frontmatter is cleaner for parsing
    
    # Escape quotes in JSON for YAML frontmatter if needed, but a block is safer
    # Let's use a delimiter for the machine readable part
    
    final_content = f"---\ndescription: {description}\ntype: {wf_type}\n---\n\n{content}\n\n<!-- WORKFLOW_STEPS_START\n{steps_json}\nWORKFLOW_STEPS_END -->"
    
    path = os.path.join(WORKFLOW_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(final_content)
        
    return True

def delete_workflow(filename):
    """Deletes a workflow file."""
    path = os.path.join(WORKFLOW_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def extract_steps_from_workflow(filename):
    """
    Extracts the JSON steps from a workflow file.
    """
    data = load_workflow(filename)
    if not data:
        return []
    
    content = data.get("content", "")
    match = re.search(r"<!-- WORKFLOW_STEPS_START\s+(.+?)\s+WORKFLOW_STEPS_END -->", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    return []
