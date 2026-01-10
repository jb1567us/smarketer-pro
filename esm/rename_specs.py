import os

DIR = r'C:\sandbox\esm\spec_sheets_v2'
for filename in os.listdir(DIR):
    if filename.endswith(".pdf"):
        # Replace spaces with hyphens, remove special chars
        new_name = filename.replace(" ", "-").replace("'", "").replace("&", "and")
        # Ensure only one _Sheet suffix
        if "_Sheet.pdf" not in new_name:
             # Should be fine from previous script
             pass
        
        old_path = os.path.join(DIR, filename)
        new_path = os.path.join(DIR, new_name)
        
        if old_path != new_path:
            os.rename(old_path, new_path)
            # print(f"Renamed {filename} -> {new_name}")

print("Renaming complete.")

import shutil
shutil.make_archive(r'C:\sandbox\esm\spec_sheets_final', 'zip', DIR)
print("Zipped to spec_sheets_final.zip")
