import os
import zipfile

INPUT_DIR = r'C:\sandbox\esm\spec_sheets_v3'
ZIP1 = 'sheets_v3_1.zip'
ZIP2 = 'sheets_v3_2.zip'

files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.pdf')])
mid = len(files) // 2
set1 = files[:mid]
set2 = files[mid:]

print(f"Total files: {len(files)}")
print(f"Set 1: {len(set1)} files -> {ZIP1}")
print(f"Set 2: {len(set2)} files -> {ZIP2}")

with zipfile.ZipFile(ZIP1, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in set1:
        z.write(os.path.join(INPUT_DIR, f), arcname=f)

with zipfile.ZipFile(ZIP2, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in set2:
        z.write(os.path.join(INPUT_DIR, f), arcname=f)

print("Done.")
