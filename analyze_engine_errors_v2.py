
import re
import collections
import os

log_files = [
    'c:\\sandbox\\b2b_outreach_tool\\live_searxng_logs.txt',
    'c:\\sandbox\\b2b_outreach_tool\\searxng_debug.log',
    'c:\\sandbox\\b2b_outreach_tool\\full_searxng_log.txt',
    'c:\\sandbox\\b2b_outreach_tool\\logs.txt',
    'c:\\sandbox\\b2b_outreach_tool\\logs_final.txt'
]

engine_errors = collections.defaultdict(int)
unique_exceptions = set()

print(f"Parsing {len(log_files)} log files...")

for log_path in log_files:
    if not os.path.exists(log_path):
        print(f"Skipping {log_path} (not found)")
        continue
        
    try:
        content = ""
        # Try a few encodings
        read_success = False
        for enc in ['utf-8', 'utf-16', 'utf-16le', 'latin-1']:
            try:
                with open(log_path, 'r', encoding=enc) as f:
                    content = f.read()
                read_success = True
                # print(f"Successfully read {log_path} with {enc}")
                break
            except UnicodeError:
                continue
        
        if not read_success:
             print(f"Failed to read {log_path} with standard encodings")
             continue

        # Regex to find engine files in traceback
        # e.g., /usr/local/searxng/searx/engines/duckduckgo.py
        # Also look for [brand name] pattern in logs if possible, but path is most reliable for errors
        matches = re.findall(r'/engines/([a-zA-Z0-9_]+)\.py', content)
        for engine in matches:
            engine_errors[engine] += 1
        
        # Look for "Engine [name] error" type messages if they exist
        # searxng often logs: "Engine 'google' ..."
        
        # Capture lines with "Exception"
        exceptions = re.findall(r'(\w+Exception):', content)
        for exc in exceptions:
            unique_exceptions.add(exc)

    except Exception as e:
        print(f"Error processing {log_path}: {e}")

print("\nEngine Error Counts (by traceback frequency):")
for engine, count in sorted(engine_errors.items(), key=lambda x: x[1], reverse=True):
    print(f"{engine}: {count}")

print("\nUnique Exceptions Found:")
for exc in unique_exceptions:
    print(exc)
