
import subprocess

def get_logs():
    try:
        result = subprocess.run(['docker-compose', 'logs', '--tail', '1000', 'searxng'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result.stdout
    except Exception as e:
        return str(e)

logs = get_logs()
lines = logs.splitlines()

found = False
for i, line in enumerate(lines):
    if "wikidata (init failed)" in line:
        found = True
        print(f"--- FAILED AT LINE {i+1} ---")
        # Go back a bit for context and forward for traceback
        start = max(0, i - 10)
        end = min(len(lines), i + 30)
        for j in range(start, end):
            prefix = ">>> " if j == i else "    "
            print(f"{prefix}{lines[j]}")
        print("-" * 30)

if not found:
    print("Pattern 'wikidata (init failed)' not found in the last 1000 lines.")
    # Try just "wikidata"
    print("\nRecent wikidata lines:")
    for line in lines[-100:]:
        if "wikidata" in line:
            print(line)
