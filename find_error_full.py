
try:
    with open("logs/crash.log", "r", encoding="utf-16le") as f:
        content = f.read()
except UnicodeError:
    with open("logs/crash.log", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

if "AttributeError" in content:
    parts = content.split("Traceback (most recent call last):")
    # Get the last traceback full block
    if len(parts) > 1:
        full_traceback = "Traceback (most recent call last):" + parts[-1]
        print(full_traceback[-3000:])
    else:
        print("AttributeError found but no Traceback header??")
else:
    print("AttributeError not found in logs/crash.log")
