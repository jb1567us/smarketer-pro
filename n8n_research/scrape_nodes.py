import requests
import json
import os

def parse_nuxt_payload(data):
    """
    Very basic parser for Nuxt _payload.json format.
    It maps index-based references to their values.
    """
    if not isinstance(data, list) or len(data) == 0:
        return data

    # The payload is usually [ {data: index}, value0, value1, ... ]
    # Values can be primitives, objects, or arrays.
    # Objects/arrays index back into the same list.
    
    # This is a complex format, but usually for integrations we just need the 
    # list of nodes which is often a large array in the middle.
    
    # Let's try a heuristic: find the largest list of objects that look like nodes.
    for item in data:
        if isinstance(item, list) and len(item) > 100:
            # Check if elements are dicts with 'name' or 'title'
            # Nuxt obfuscates this further, but let's see.
            pass

    return data # Fallback

def get_n8n_integrations():
    print("Fetching n8n integrations payload...")
    url = "https://n8n.io/integrations/_payload.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch: {resp.status_code}")
            return None
            
        payload = resp.json()
        
        # Nuxt payload parsing is non-trivial. 
        # Instead of writing a full recursive parser, we'll extract the 
        # raw strings and objects and filter for node-like things.
        
        # The payload contains a manifest. 
        # Often the integrations are in a flat list or nested under a key.
        
        # Heuristic: Find all strings that look like node names or keys.
        # Nodes usually have URLs like /integrations/salesforce/
        
        integrations = []
        
        # Let's look for strings that start with /integrations/ and don't end in /
        all_paths = [s for s in payload if isinstance(s, str) and s.startswith("/integrations/") and s != "/integrations/"]
        
        for path in all_paths:
            name = path.replace("/integrations/", "").replace("/", " ").title()
            integrations.append({
                "name": name,
                "url": f"https://n8n.io{path}",
                "type": "node"
            })
            
        print(f"Extracted {len(integrations)} potential integrations.")
        return integrations

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    integrations = get_n8n_integrations()
    if integrations:
        output_file = os.path.join("n8n_research", "n8n_nodes.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(integrations, f, indent=2)
        print(f"Saved {len(integrations)} nodes to {output_file}")

if __name__ == "__main__":
    main()
