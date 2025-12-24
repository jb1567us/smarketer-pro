import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urls = [
    'https://elliotspencermorgan.com/caviarpainting/',
    'https://elliotspencermorgan.com/boldpainting-4/',
    'https://elliotspencermorgan.com/floating_6_-_rabbitsculpture/',
    'https://elliotspencermorgan.com/floating_6_-_rabbitSculpture/'
]

with open('verification_results.txt', 'w') as f:
    for u in urls:
        try:
            code = requests.get(u, verify=False).status_code
            f.write(f'{u}: {code}\n')
        except Exception as e:
            f.write(f'{u}: Error {e}\n')
