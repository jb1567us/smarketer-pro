
import re
import collections

log_files = [
    'c:\\sandbox\\b2b_outreach_tool\\live_searxng_logs.txt',
    # 'c:\\sandbox\\b2b_outreach_tool\\searxng_debug.log'
]

engine_errors = collections.defaultdict(int)
unique_exceptions = set()

for log_path in log_files:
    try:
        # Try utf-16 first for live logs
        try:
            with open(log_path, 'r', encoding='utf-16') as f:
                content = f.read()
        except UnicodeError:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        # Regex to find engine files in traceback
        # e.g., /usr/local/searxng/searx/engines/duckduckgo.py
        matches = re.findall(r'/engines/([a-zA-Z0-9_]+)\.py', content)
        for engine in matches:
            engine_errors[engine] += 1
        
        # Look for explicit exception names near engine mentions ??
        # Or just capture lines with "Exception"
        exceptions = re.findall(r'(\w+Exception):', content)
        for exc in exceptions:
            unique_exceptions.add(exc)

    except Exception as e:
        print(f"Error reading {log_path}: {e}")

print("Engine Error Counts:")
for engine, count in sorted(engine_errors.items(), key=lambda x: x[1], reverse=True):
    print(f"{engine}: {count}")

print("\nUnique Exceptions Found:")
for exc in unique_exceptions:
    print(exc)
