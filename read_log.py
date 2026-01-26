
try:
    with open("app.log", "r", encoding="utf-16le") as f:
        content = f.read()
except UnicodeError:
    with open("app.log", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

lines = content.splitlines()
print(f"Total lines: {len(lines)}")
# Print the last 100 lines
for line in lines[-100:]:
    print(line)
