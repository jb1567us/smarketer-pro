import shutil
import os

source = r'C:\sandbox\esm\spec_sheets'
target = r'C:\sandbox\esm\spec_sheets'

# Remove existing if any
if os.path.exists(target + '.zip'):
    os.remove(target + '.zip')

shutil.make_archive(target, 'zip', source)
print(f"Created {target}.zip")
