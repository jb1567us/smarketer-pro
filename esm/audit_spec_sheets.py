import os

DIR = r'C:\sandbox\esm\spec_sheets_v3'
THRESHOLD = 25000 # 25KB

files = sorted(os.listdir(DIR))
missing = []
valid = []

print(f"Auditing {len(files)} spec sheets in {DIR}...\n")

for f in files:
    if not f.endswith('.pdf'): continue
    path = os.path.join(DIR, f)
    size = os.path.getsize(path)
    
    if size < THRESHOLD:
        missing.append(f"{f} ({size} bytes)")
    else:
        valid.append(f)

print(f"✅ Found {len(valid)} valid spec sheets (images likely present).")
print(f"❌ Found {len(missing)} sheets with missing images (placeholder size):")
for m in missing:
    print(f" - {m}")
