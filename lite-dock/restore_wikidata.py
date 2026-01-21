import os

# Path to the deleted file
target_path = r"C:\Users\baron\.litedock\images\searxng_searxng_latest\usr\local\searxng\searx\engines\wikidata.py"

# Minimal content to satisfy imports but do nothing (NO IMPORTS)
dummy_content = """
# Minimal attributes to satisfy registry
categories = ['general']
paging = False
language_support = True

# --- Dummy Exports for other engines ---
def send_wikidata_query(query, **kwargs): return {}
def sparql_string_escape(s): return s
def get_thumbnail(result): return None
# ---------------------------------------

def init(engine_settings):
    # Do nothing, immediately succeed
    return True

def request(query, params):
    # Return empty results immediately
    return {'url': 'https://www.wikidata.org/', 'data': {}}

def response(resp):
    return []
"""

def restore():
    print(f"Restoring dummy wikidata.py to {target_path}...")
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(dummy_content)
        print("✅ Restored successfully.")
    except Exception as e:
        print(f"❌ Failed to restore: {e}")

if __name__ == "__main__":
    restore()
