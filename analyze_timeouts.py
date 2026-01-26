
import re
import os

log_files = [
    'c:\\sandbox\\b2b_outreach_tool\\live_searxng_logs.txt',
    'c:\\sandbox\\b2b_outreach_tool\\searxng_debug.log',
    'c:\\sandbox\\b2b_outreach_tool\\full_searxng_log.txt',
    'c:\\sandbox\\b2b_outreach_tool\\logs.txt'
]

timeout_counts = 0
timeout_engines = set()

print("Scanning for Timeouts...")

for log_path in log_files:
    if not os.path.exists(log_path):
        continue
        
    try:
        content = ""
        read_success = False
        for enc in ['utf-8', 'utf-16', 'utf-16le', 'latin-1']:
            try:
                with open(log_path, 'r', encoding=enc) as f:
                    content = f.read()
                read_success = True
                break
            except UnicodeError:
                continue
        
        if not read_success:
             continue
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "Timeout" in line or "timed out" in line.lower():
                timeout_counts += 1
                # Check previous/next lines for context (engine name)
                context = "\n".join(lines[max(0, i-5):min(len(lines), i+5)])
                # Look for engine py file in context
                matches = re.findall(r'/engines/([a-zA-Z0-9_]+)\.py', context)
                for engine in matches:
                    timeout_engines.add(engine)
                # print(f"Found timeout in {log_path}: {line.strip()}")

    except Exception as e:
        print(f"Error processing {log_path}: {e}")

print(f"Total Timeout occurrences: {timeout_counts}")
if timeout_engines:
    print(f"Engines associated with timeouts: {', '.join(timeout_engines)}")
else:
    print("No specific engines associated with timeouts found in context.")
