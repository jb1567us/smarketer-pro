import sqlite3
import time
import json
import random
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from database import (
    get_connection, init_db, add_lead, save_agent_work_product,
    create_chat_session, save_chat_message, DB_PATH
)
from affiliate_system import AffiliateManager

def get_robust_connection():
    return sqlite3.connect(DB_PATH, timeout=30)

def execute_with_retry(query, params=(), is_many=False):
    """Executes a query with retry logic for locked databases."""
    for attempt in range(5):
        try:
            conn = get_robust_connection()
            c = conn.cursor()
            if is_many:
                c.executemany(query, params)
            else:
                c.execute(query, params)
            conn.commit()
            last_id = c.lastrowid
            conn.close()
            return last_id
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"⚠️ Database locked, retrying (attempt {attempt+1}/5)...")
                time.sleep(random.uniform(1, 3))
            else:
                raise e
    print(f"❌ Failed to execute query after 5 attempts due to lock.")
    return None

def seed_database():
    print("🚀 Initializing Database...")
    init_db()

    # 1. Niches and Pain Points
    print("📌 Seeding Pain Points & Campaigns...")
    niches = [
        {"name": "SaaS for HR", "product": "TalentFlow AI", "desc": "AI-powered recruiting automation"},
        {"name": "E-commerce Logistics", "product": "ShipSwift", "desc": "Reduced shipping costs for Shopify stores"},
        {"name": "Solar Installers", "product": "SunGrowth CRM", "desc": "High-intent lead gen for solar contractors"}
    ]

    campaign_ids = []
    for niche in niches:
        # Create Campaign
        cid = execute_with_retry('''
            INSERT INTO campaigns (name, niche, product_name, product_context, status, created_at)
            VALUES (?, ?, ?, ?, 'active', ?)
        ''', (f"Growth Campaign - {niche['name']}", niche['name'], niche['product'], niche['desc'], int(time.time())))
        if cid: campaign_ids.append(cid)

        # Add Pain Points
        ppp = [
            (niche['name'], f"High Churn in {niche['name']}", "Companies are losing customers faster than they can acquire them.", int(time.time())),
            (niche['name'], f"Inefficient Scaling", "Manual processes are slowing down growth.", int(time.time()))
        ]
        execute_with_retry('INSERT INTO pain_points (niche, pain_point, description, created_at) VALUES (?, ?, ?, ?)', ppp, is_many=True)
        
        if cid:
            execute_with_retry('UPDATE campaigns SET selected_pain_point_id = (SELECT id FROM pain_points WHERE niche = ? LIMIT 1) WHERE id = ?', (niche['name'], cid))

    # 2. WordPress Site & DSR
    print("🌐 Seeding WordPress Site (lookoverhere.xyz/dsr-test)...")
    site_id = execute_with_retry('''
        INSERT INTO wp_sites (name, url, username, app_password, cpanel_url, cpanel_user, cpanel_pass, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("Main Test Site", "https://lookoverhere.xyz/dsr-test", "admin", "dummy_app_pass", "https://lookoverhere.xyz:2083", "cpanel_user", "cpanel_pass", int(time.time())))

    # 3. Leads
    print("👥 Seeding Leads...")
    industries = ["Technology", "Retail", "Manufacturing", "Energy"]
    leads_to_add = []
    for i in range(50):
        niche = random.choice(niches)
        industry = random.choice(industries)
        email = f"lead_{i}@example{random.randint(1,100)}.com"
        
        # add_lead has its own internal retry/timeout now via database.py
        lead_id = add_lead(
            url=f"https://company{i}.com",
            email=email,
            source="dummy_generator",
            category=niche['name'],
            industry=industry,
            company_name=f"Big Corp {i}",
            confidence=round(random.uniform(0.7, 0.99), 2)
        )
        if lead_id:
            status = random.choice(['new', 'contacted', 'replied', 'nurtured', 'error'])
            execute_with_retry('UPDATE leads SET status = ? WHERE id = ?', (status, lead_id))
            if campaign_ids:
                leads_to_add.append((random.choice(campaign_ids), lead_id))

    # 4. Digital Sales Rooms (DSR)
    if site_id:
        print("🚪 Seeding Digital Sales Rooms...")
        for cid, lid in leads_to_add[:5]:
            execute_with_retry('''
                INSERT INTO digital_sales_rooms (campaign_id, lead_id, site_id, title, slug, content_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'published', ?)
            ''', (cid, lid, site_id, f"Custom Proposal for Corp {lid}", f"proposal-{lid}", json.dumps({"hero": "Welcome", "body": "Value proposition details..."}), int(time.time())))

    # 5. Campaign Events
    print("📈 Seeding Campaign Events...")
    for cid, lid in leads_to_add[:20]:
        events = [
            (f"lead_{lid}@example.com", lid, cid, 'sent', int(time.time() - 86400)),
            (f"lead_{lid}@example.com", lid, cid, 'open', int(time.time() - 43200))
        ]
        execute_with_retry('INSERT INTO campaign_events (lead_email, lead_id, campaign_id, event_type, timestamp) VALUES (?, ?, ?, ?, ?)', events, is_many=True)

    # 6. CRM Data
    print("💼 Seeding CRM Data...")
    stages = ['Discovery', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won']
    for i in range(10):
        if leads_to_add:
            lid = random.choice(leads_to_add)[1]
            execute_with_retry('''
                INSERT INTO deals (lead_id, title, value, stage, probability, close_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (lid, f"Deal with Corp {lid}", random.randint(1000, 50000), random.choice(stages), random.randint(20, 90), int(time.time() + 2592000), int(time.time())))
            
            execute_with_retry('''
                INSERT INTO tasks (lead_id, description, due_date, priority, task_type, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (lid, f"Follow up call for Corp {lid}", int(time.time() + 86400), random.choice(['Low', 'Medium', 'High']), 'Call', 'pending', int(time.time())))

    # 7. Agent Work Products, Affiliate, Chat (Skipped or wrapped if needed)
    # These functions use get_connection() which now has 30s timeout.
    try:
        print("🤖 Seeding Agent Work History...")
        for i in range(10):
            save_agent_work_product("Researcher", f"Task {i}", "Dummy content", ["test"])
            
        print("🔗 Seeding Affiliate Data...")
        am = AffiliateManager()
        am.generate_dummy_data()

        print("💬 Seeding Chat Sessions...")
        sid = create_chat_session("Seeding Hub")
        save_chat_message(sid, "user", "Hello")
    except Exception as e:
        print(f"⚠️ Minor error in non-core seeding: {e}")

    print("\n✅ Seeding Complete! (with robust retry logic)")

if __name__ == "__main__":
    seed_database()
