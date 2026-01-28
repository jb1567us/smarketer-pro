import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.mcp.hub_server import list_resources, fetch_resource_logic

async def main():
    print("Verifying MCP Directives Integration...")
    
    # 1. List Resources
    resources = await list_resources()
    print(f"Found {len(resources)} resources.")
    
    directive_uris = [str(r.uri) for r in resources if str(r.uri).startswith("directive://")]
    print(f"Found {len(directive_uris)} directive resources.")
    
    if not directive_uris:
        print("❌ No directives found!")
        sys.exit(1)
        
    print("Sample URIs:")
    for uri in directive_uris[:5]:
        print(f" - {uri}")
        
    # 2. Test Fetch
    test_uri = directive_uris[0]
    print(f"\nTesting fetch for: {test_uri}")
    content = await fetch_resource_logic(test_uri)
    
    if content and not content.startswith("ERROR"):
        print(f"✅ Successfully read content ({len(content)} bytes).")
        print("Preview:", content[:100].replace("\n", " "))
    else:
        print(f"❌ Failed to read content: {content}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
