
try:
    with open(r"c:\sandbox\b2b_outreach_tool\logs\crash.log", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    tracebacks = content.split("Traceback (most recent call last):")
    if len(tracebacks) > 1:
        last_traceback = "Traceback (most recent call last):" + tracebacks[-1]
        print(last_traceback[-2000:]) # Print last 2000 chars of the traceback
    else:
        print("No traceback found.")
        
except Exception as e:
    print(f"Error: {e}")
