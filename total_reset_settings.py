import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

MINIMAL_CONFIG = """
general:
  debug: false
  instance_name: "SearXNG Optimized"
  donation_url: false
  contact_url: false
  enable_metrics: true

brand:
  new_issue_url: https://github.com/searxng/searxng/issues/new
  docs_url: https://docs.searxng.org/

search:
  safe_search: 0
  autocomplete: ""
  default_lang: "auto"
  formats:
    - html
    - json

server:
  port: 8080
  bind_address: "0.0.0.0"
  secret_key: "OUSSu4yLt3EUvH186uLJIpZyzpgB5kg"
  image_proxy: false
  method: "GET"

ui:
  static_path: ""
  templates_path: ""
  default_theme: simple
  theme_args:
    simple_style: auto

# THE CLEAN OUTGOING BLOCK
outgoing:
  request_timeout: 20.0
  max_request_timeout: 30.0
  pool_connections: 100
  pool_maxsize: 100
  enable_http2: true
  networks:
    direct:
      local_addresses:
        - 0.0.0.0
    yandex: {}
    brave: {}
    yacy: {}
    seekr: {}

# ENABLE ONLY ESSENTIAL ENGINES FOR TESTING
engines:
  - name: wikidata
    engine: wikidata
    shortcut: wd
    categories: [general]
    timeout: 15.0
    network: direct
    disabled: false

  - name: wikipedia
    engine: wikipedia
    shortcut: wp
    categories: [general]
    network: direct

  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    categories: [general]
    network: direct

  - name: google
    engine: google
    shortcut: go
    categories: [general]
    disabled: true # To avoid immediate blocks during testing
    network: direct

enabled_plugins:
  - 'Basic Pager'
  - 'Hash plugin'
  - 'Self Info'

# END OF CONFIG
"""

def total_reset():
    print(f"Total reset of {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.write(MINIMAL_CONFIG.strip())
    print("Done.")

if __name__ == "__main__":
    total_reset()
