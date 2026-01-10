import requests
from PIL import Image
from io import BytesIO

def get_logo_size():
    url = "https://elliotspencermorgan.com/logo.png"
    try:
        response = requests.get(url, verify=False, timeout=10)
        img = Image.open(BytesIO(response.content))
        print(f"Dimensions: {img.size[0]}x{img.size[1]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    get_logo_size()
