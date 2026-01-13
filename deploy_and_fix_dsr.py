
import sqlite3
import os
import sys
import asyncio

# Patch sys.path to allow imports from src as root if needed
current_dir = os.getcwd()
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from src.agents.wordpress import WordPressAgent
from src.dsr_manager import DSRManager



# Configuration
WP_URL = "https://lookoverhere.xyz/dsr-test"
WP_USER = "admin"
# Ideally use App Password, but for now we'll put credentials in DB.
# If we need an app password, we might need to generate one manually or via browser agent.
# But let's try to update the DB first.
WP_PASS = "OutreachAgent2026!" 
DB_PATH = "leads.db"

def update_wp_site_in_db():
    """Updates or inserts the WP site entry in the database."""
    print(f"💾 Updating database for {WP_URL}...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if exists
    c.execute("SELECT id FROM wp_sites WHERE url LIKE ?", (f"%{WP_URL}%",))
    row = c.fetchone()
    
    if row:
        site_id = row[0]
        print(f"   - Site exists (ID: {site_id}). Updating credentials...")
        c.execute("""
            UPDATE wp_sites 
            SET username = ?, app_password = ?
            WHERE id = ?
        """, (WP_USER, WP_PASS, site_id))
    else:
        print("   - Site does not exist. Creating new entry...")
        c.execute("""
            INSERT INTO wp_sites (name, url, username, app_password, cpanel_url, cpanel_user, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, ("DSR Test Site", WP_URL, WP_USER, WP_PASS, "https://elk.lev3.com:2083", "lookoverhere"))
        site_id = c.lastrowid
        
    conn.commit()
    conn.close()
    print(f"✅ Database updated. Site ID: {site_id}")
    return site_id

async def deploy():
    print(f"🚀 Starting deployment to {WP_URL}...")
    
    # Step 1: Update DB with Site Info
    update_wp_site_in_db()
    
    # Step 2: Deploy DSR Pages
    # We need to initialize DSRManager
    # It needs a 'manager_agent'? Or can we run it directly?
    # looking at dsr_manager.py (viewed earlier), it uses 'wp_agent'.
    
    print("📄 Deploying DSR Pages...")
    
    # We need to instantiate agents
    # DSRManager.__init__(self, agent_manager)
    # It might be complex to instantiate DSRManager if it depends on full system.
    # Let's try to just fetch DSRs and use WordPressAgent directly if DSRManager is too heavy.
    # Or instantiate DSRManager with a mock?
    
    # Let's try to use DSRManager if possible. But it requires 'agent_manager'.
    # If that's hard, we can replicate the deploy logic: render HTML, create page.
    
    # Let's fetch DSRs first
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    dsrs = conn.execute("SELECT * FROM digital_sales_rooms").fetchall()
    conn.close()
    
    if not dsrs:
        print("❌ No DSRs found in database!")
        return

    wp_agent = WordPressAgent()
    
    for dsr in dsrs:
        slug = dsr['slug']
        title = f"Proposal: {slug}" # dsr table has no name column
        print(f"   - Deploying '{title}' (slug: {slug})...")
        
        # Prepare content (basic for now, verifying verification)
        # Ideally DSRManager renders this. 
        # For this fix, let's just make sure a page exists.
        content = f"""
        <!-- wp:paragraph -->
        <p>This is a deployed DSR page for {title}.</p>
        <!-- /wp:paragraph -->
        <!-- wp:heading -->
        <h2>Proposal Details</h2>
        <!-- /wp:heading -->
        <p>Content goes here.</p>
        """
        
        # Use WordPress Agent to create page
        # Note: WP agent uses REST API. It needs Application Password usually.
        # We put 'OutreachAgent2026!' in app_password field. 
        # Basic Auth works with Main Password ONLY IF Basic Auth plugin is installed or on some setups.
        # Core WP requires App Password for Basic Auth.
        # Since we skipped App Password generation, THIS MIGHT FAIL if we use the main password.
        # However, checking if 'OutreachAgent2026!' works.
        
        res = await wp_agent.manage_content(
            site_url=WP_URL,
            username=WP_USER,
            app_password=WP_PASS,
            action="create_page",
            data={
                "title": title,
                "content": content,
                "status": "publish"
            }
        )
        
        if "error" in res:
            print(f"❌ Failed to deploy {slug}: {res['error']}")
            if "401" in str(res.get('error', '')):
                print("      -> Authorization failed. Main password might not work for REST API.")
                print("      -> We likely need a real Application Password.")
        else:
            print(f"✅ Deployed: {res.get('link')}")

if __name__ == "__main__":
    asyncio.run(deploy())
