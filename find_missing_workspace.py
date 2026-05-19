import ast

with open('d:/sandbox/smarketer-pro/src/database.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

tables_with_workspace = [
    'leads', 'campaigns', 'deals', 'tasks', 'creative_content',
    'email_templates', 'campaign_events', 'email_logs', 'sequences', 
    'sequence_steps', 'sequence_enrollments', 'custom_agents', 
    'strategy_presets', 'scheduled_posts', 'chat_sessions', 
    'agent_decisions', 'agent_work_products', 'wp_sites', 
    'digital_sales_rooms', 'link_wheels', 'my_affiliate_programs', 
    'my_affiliate_links', 'partners', 'partner_contracts', 'partner_events',
    'payouts', 'registration_tasks', 'registration_macros', 'managed_accounts',
    'chat_messages'
]

functions_to_fix = []

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # check if it does SQL operations
        source_str = ast.get_source_segment(source, node)
        if source_str is None:
            continue
            
        # Does it interact with a table that needs workspace_id?
        # A simple check: if any of the table names appear in the source text of the function.
        # AND it's a SELECT, INSERT, UPDATE, DELETE snippet.
        has_table = any(table in source_str for table in tables_with_workspace)
        is_sql = 'INSERT ' in source_str.upper() or 'SELECT ' in source_str.upper() or 'UPDATE ' in source_str.upper() or 'DELETE ' in source_str.upper()
        
        if has_table and is_sql:
            # Check if function takes workspace_id
            args = [arg.arg for arg in node.args.args]
            if 'workspace_id' not in args:
                # To reduce noise, make sure we only flag if it actually uses the table in a SQL query
                functions_to_fix.append((node.name, node.lineno, node.end_lineno))

print("Functions needing check:")
for f in functions_to_fix:
    print(f"- {f[0]} (lines {f[1]}-{f[2]})")

