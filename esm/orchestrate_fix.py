import requests
import os

# Configuration
URL = "https://elliotspencermorgan.com/fix_images_remote.php"
LOCAL_IMG_DIR = r"c:\sandbox\esm\09\09"

# Mapping: Page Title -> Filename
# Note: Filenames based on what we found in 09\09
TASKS = [
    ("City at Night Mulch Series", "City_at_Night_-_Mulch_SeriesCollage.jpg"),
    ("Close up Mulch Series", "Close_up_-_Mulch_SeriesCollage.jpg"),
    ("Red and Black Mulch Series", "Red_and_Black_-_Mulch_SeriesCollage.jpg"),
    ("Megapixels", "MegapixelsSculpture.jpg"),
    ("Existance", "ExistancePainting.jpg"), # Spelling as per user request
]

def run_fix():
    for page_title, filename in TASKS:
        file_path = os.path.join(LOCAL_IMG_DIR, filename)
        if not os.path.exists(file_path):
            print(f"[SKIP] File not found: {file_path}")
            continue
            
        print(f"Processing '{page_title}' with image '{filename}'...")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'image/jpeg')}
                data = {
                    'action': 'upload_and_attach',
                    'page_title': page_title
                }
                
                # Disable verify=False warning if needed, or just ignore
                response = requests.post(URL, data=data, files=files, verify=False, timeout=60)
                
                if response.status_code == 200:
                    try:
                        res_json = response.json()
                        print(f"  Result: {res_json}")
                    except ValueError:
                        print(f"  Non-JSON Response: {response.text[:200]}")
                else:
                     print(f"  HTTP Error {response.status_code}: {response.text}")
                     
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    run_fix()
