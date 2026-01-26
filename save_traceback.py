
try:
    with open("logs/crash.log", "r", encoding="utf-16le") as f:
        content = f.read()
except UnicodeError:
    with open("logs/crash.log", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

if "AttributeError" in content:
    parts = content.split("Traceback (most recent call last):")
    if len(parts) > 1:
        full_traceback = "Traceback (most recent call last):" + parts[-1]
        # Write to file
        with open("traceback.txt", "w", encoding="utf-8") as f_out:
            f_out.write(full_traceback[-5000:])
        print("Traceback written to traceback.txt")
    else:
        print("No traceback block found")
else:
    print("AttributeError not found")
