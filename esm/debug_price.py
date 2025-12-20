import requests
import re

url = 'https://www.saatchiart.com/art/Painting-Portal-2/1295487/8146546/view'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
r = requests.get(url, headers=headers)

print(f"Status: {r.status_code}")
content = r.text

indices = [m.start() for m in re.finditer('USD', content)]
for i in indices:
    print(f"\nCONTEXT at {i}:")
    print(content[i-100:i+100])

indices_price = [m.start() for m in re.finditer('"price"', content)]
for i in indices_price:
    print(f"\nPRICE CONTEXT at {i}:")
    print(content[i:i+100])
