import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

STABLE_NO_WIKIDATA = """
general:
  debug: false
  instance_name: "SearXNG Isolation Test"
  enable_metrics: false

brand:
  new_issue_url: https://github.com/searxng/searxng/issues/new

search:
  safe_search: 0
  autocomplete: ""
  default_lang: "auto"
  formats: [html, json]

server:
  port: 8080
  bind_address: "0.0.0.0"
  secret_key: "OUSSu4yLt3EUvH186uLJIpZyzpgB5kg"
  image_proxy: false
  method: "GET"

ui:
  default_theme: simple

outgoing:
  request_timeout: 30.0

engines:
  - name: wikidata
    engine: wikidata
    disabled: true

  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    categories: [general]
    disabled: false
"""

def isolation_test():
    print(f"Applying isolation test config to {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(STABLE_NO_WIKIDATA.strip() + "\n")
    print("Done.")

if __name__ == "__main__":
    isolation_test()
