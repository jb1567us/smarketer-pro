import json
import requests
import re
import time
import os

file_path = 'c:/sandbox/esm/artwork_data.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

updated_count = 0
errors = 0

print(f"Total items: {len(data)}")

for item in data:
    if 'saatchi_url' not in item or not item['saatchi_url']:
        continue
    
    # Optional: Skip if price already exists? User said "Verify prices", so maybe we should check all?
    # User said "Verify the prices of all... in the same manner".
    # Logic: If price exists, we can still check it, but let's prioritize missing ones.
    # Actually, let's just do all of them because prices might have changed.
    
    url = item['saatchi_url']
    title = item.get('title', 'Unknown')
    
    print(f"Checking {title}...", end='', flush=True)
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            # Pattern 1: Meta description "Price is X USD"
            # <meta name="description" content="... Price is 355 USD. ...">
            # <meta property="og:description" content="... Price is 355 USD. ...">
            
            # Specific JSON pattern: "price":{"currency":"USD","amount":460}
            match = re.search(r'"price":\{"currency":"USD","amount":([\d\.]+)\}', r.text)
            if match:
                price = str(int(float(match.group(1)))) # Convert to int str, handle 460.0
                old_price = item.get('price', 'None')
                if old_price == price:
                     print(f" Verified: ${price}")
                else:
                     item['price'] = price
                     print(f" UPDATED: ${price} (Was: {old_price})")
                     updated_count += 1
            else:
                # Fallback: "price":460,"availability"
                match2 = re.search(r'"price":(\d+),"availability"', r.text)
                if match2:
                    price = match2.group(1)
                    old_price = item.get('price', 'None')
                    if old_price == price:
                         print(f" Verified: ${price}")
                    else:
                         item['price'] = price
                         print(f" UPDATED (Fallback): ${price} (Was: {old_price})")
                         updated_count += 1
                else:
                    print(" Price pattern NOT found.")
        else:
            print(f" Failed (Status {r.status_code})")
            errors += 1
            
    except Exception as e:
        print(f" Error: {e}")
        errors += 1
        
    time.sleep(1) # Be polite

print(f"\nUpdated {updated_count} items. {errors} errors.")

# Save
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
