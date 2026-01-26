import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

ULTRA_MINIMAL = """
general:
  debug: false
  instance_name: "SearXNG Direct Test"
  enable_metrics: true

server:
  port: 8080
  bind_address: "0.0.0.0"
  secret_key: "OUSSu4yLt3EUvH186uLJIpZyzpgB5kg"

search:
  formats:
    - html
    - json

outgoing:
  request_timeout: 30.0
"""

def ultra_minimal_reset():
    print(f"Ultra-minimal reset of {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.write(ULTRA_MINIMAL.strip())
    print("Done.")

if __name__ == "__main__":
    ultra_minimal_reset()
