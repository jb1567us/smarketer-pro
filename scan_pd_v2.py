import ast

FILE_PATH = r"c:\sandbox\b2b_outreach_tool\src\ui\agent_lab_ui.py"

def scan_full_pd():
    with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'render_agent_interaction_area':
            print(f"Scanning function {node.name}...")
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Name) and subnode.id == 'pd':
                    print(f"Line {subnode.lineno}: ctx={type(subnode.ctx).__name__}")
                elif isinstance(subnode, ast.alias) and subnode.asname == 'pd':
                    print(f"Line {subnode.lineno}: IMPORT AS 'pd'")
                elif isinstance(subnode, (ast.Import, ast.ImportFrom)):
                    for alias in subnode.names:
                        if alias.name == 'pd' or alias.asname == 'pd':
                            print(f"Line {subnode.lineno}: {type(subnode).__name__} mentions 'pd'")

if __name__ == "__main__":
    scan_full_pd()
