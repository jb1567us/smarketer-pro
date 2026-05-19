import ast
import re

with open('src/database.py', encoding='utf-8') as f:
    code = f.read()

tables = [
    'leads', 'campaigns', 'deals', 'tasks', 'creative_content',
    'email_templates', 'campaign_events', 'email_logs', 'sequences', 
    'sequence_steps', 'sequence_enrollments', 'custom_agents', 
    'strategy_presets', 'scheduled_posts', 'chat_sessions', 
    'agent_decisions', 'agent_work_products', 'wp_sites', 
    'digital_sales_rooms', 'link_wheels', 'my_affiliate_programs', 
    'my_affiliate_links', 'partners', 'partner_contracts', 
    'partner_events', 'payouts', 'managed_accounts', 'registration_tasks', 
    'registration_macros'
]

class Extractor(ast.NodeVisitor):
    def __init__(self):
        self.targets = []
    def visit_FunctionDef(self, node):
        if node.name in ('init_db', 'get_connection'):
            return
        needs_update = False
        for n in ast.walk(node):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ('execute', 'executemany'):
                if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                    sql = n.args[0].value.lower()
                    for t in tables:
                        if re.search(r'\b' + t + r'\b', sql):
                            needs_update = True
                            break
        if needs_update:
            self.targets.append((node.lineno, node.end_lineno, node.name))
            
        self.generic_visit(node)

ext = Extractor()
ext.visit(ast.parse(code))
with open('targets.txt', 'w', encoding='utf-8') as f:
    for t in ext.targets:
        f.write(f'{t[0]}:{t[1]}:{t[2]}\n')
print(f"Found {len(ext.targets)} functions")
