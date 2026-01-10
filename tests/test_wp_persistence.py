from database import init_db, save_wp_site, get_wp_sites, delete_wp_site
import os

def test_persistence():
    print("Testing WordPress Site Persistence...")
    
    # Ensure DB is initialized
    init_db()
    
    # 1. Save a site
    print("Saving test site...")
    save_wp_site("Test Project", "https://test.com", "admin", "pass123", "https://cp.test.com", "cpuser", "cppass")
    
    # 2. Get sites
    sites = get_wp_sites()
    print(f"Found {len(sites)} sites.")
    test_site = next((s for s in sites if s['name'] == "Test Project"), None)
    
    if test_site:
        print(f"✅ Found Test Project: {test_site['url']}")
        
        # 3. Update site
        print("Updating test site...")
        save_wp_site("Test Project", "https://updated.com", "admin", "newpass", "https://cp.test.com", "cpuser", "cppass")
        sites = get_wp_sites()
        updated_site = next((s for s in sites if s['name'] == "Test Project"), None)
        if updated_site['url'] == "https://updated.com":
            print("✅ Update successful.")
        else:
            print("❌ Update failed.")
            
        # 4. Delete site
        print("Deleting test site...")
        delete_wp_site(test_site['id'])
        sites = get_wp_sites()
        if not any(s['name'] == "Test Project" for s in sites):
            print("✅ Delete successful.")
        else:
            print("❌ Delete failed.")
    else:
        print("❌ Test Project not found.")

if __name__ == "__main__":
    # Add src to path
    import sys
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    test_persistence()
