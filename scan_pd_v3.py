import ast

FILE_PATH = r"c:\sandbox\b2b_outreach_tool\src\ui\agent_lab_ui.py"

def scan_pd_everywhere():
    with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == 'pd':
            if isinstance(node.ctx, ast.Store):
                print(f"STORE to 'pd' at line {node.lineno}")
        elif isinstance(alias := getattr(node, 'asname', None), str) and alias == 'pd':
             print(f"IMPORT AS 'pd' at line {node.lineno}")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for n in node.names:
                if n.name == 'pd' or n.asname == 'pd':
                    print(f"IMPORT mentions 'pd' at line {node.lineno}")

if __name__ == "__main__":
    scan_pd_everywhere()
