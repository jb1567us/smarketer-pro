
try:
    with open("logs/crash.log", "r", encoding="utf-16le") as f:
        content = f.read()
except UnicodeError:
    with open("logs/crash.log", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

if "AttributeError" in content:
    parts = content.split("AttributeError")
    # Take the last occurrence and the 500 chars before it
    last_part = parts[-2][-1000:] + "AttributeError" + parts[-1][:200]
    print(last_part)
else:
    print("AttributeError not found in logs/crash.log")
