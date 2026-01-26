import ast

FILE_PATH = r"c:\sandbox\b2b_outreach_tool\src\ui\agent_lab_ui.py"

def scan_for_pd_shadowing():
    with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'render_agent_interaction_area':
            print(f"Scanning function {node.name}...")
            # Find all assignments to pd in this function
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Name) and subnode.id == 'pd':
                    if isinstance(subnode.ctx, ast.Store):
                        print(f"STORE to 'pd' found at line {subnode.lineno}")
                    elif isinstance(subnode.ctx, ast.Del):
                        print(f"DELETE to 'pd' found at line {subnode.lineno}")
                elif isinstance(subnode, ast.alias) and subnode.asname == 'pd':
                    print(f"IMPORT AS 'pd' found at line {subnode.lineno}")

if __name__ == "__main__":
    scan_for_pd_shadowing()
