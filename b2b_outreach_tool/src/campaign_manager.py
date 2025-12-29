import sys
import os
import argparse
import time

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, save_pain_points, get_pain_points, save_template, get_templates, get_leads_by_status, mark_contacted
from researcher import research_niche
from copywriter import generate_campaign_sequence
from mailer import Mailer
from config import config

# UI Wrappers
def start_campaign_step_research(niche):
    pain_points = get_pain_points(niche)
    if not pain_points:
        pain_points = research_niche(niche)
        save_pain_points(niche, pain_points)
        # Re-fetch to get IDs
        pain_points = get_pain_points(niche)
    return pain_points

def start_campaign_step_copy(niche, pain_point, product_name, product_description):
    # Check for existing
    # Simplified for UI: always regen or fetch first check
    sequence = generate_campaign_sequence(niche, pain_point, product_name, product_description)
    return sequence

def start_campaign_step_send(leads, confirmation=False):
    # This logic sits simpler in the UI direct call or we abstract generic send here
    pass

def run_campaign(niche, product_name, product_description, send=False, auto=False):
    print(f"=== Starting Campaign for '{niche}' ===")
    
    # 1. Research / Load Pain Points
    pain_points = get_pain_points(niche)
    if not pain_points:
        print("No pain points found in DB. Researching...")
        pain_points_data = research_niche(niche)
        if not pain_points_data:
            print("Research failed. Exiting.")
            return
        save_pain_points(niche, pain_points_data)
        pain_points = get_pain_points(niche) # Reload with IDs
    
    print(f"\nFound {len(pain_points)} pain points:")
    for i, p in enumerate(pain_points):
        print(f"{i+1}. {p['title']}")
        
    # 2. Select Pain Point
    if auto:
        print("\n[Auto] Selecting top pain point.")
        idx = 0
    else:
        idx = int(input("\nSelect a pain point to target (number): ")) - 1
    target_pain = pain_points[idx]
    
    # 3. Generate / Load Content
    templates = get_templates(niche, stage="intro")
    # For simplicity in this CLI, we just check if we have ANY templates for this pain point
    # Ideally we strictly filter by pain_point_id, but database.py get_templates is simple.
    
    # Check if we have templates for this specific pain point
    # We will generate if not found
    points_templates = [t for t in templates if t['pain_point_id'] == target_pain['id']]
    
    if not points_templates:
        print("\nNo templates found for this pain point. Generating Copy...")
        sequence = generate_campaign_sequence(niche, target_pain, product_name, product_description)
        for email in sequence:
            save_template(niche, target_pain['id'], email['stage'], email['subject'], email['body'])
        print("Templates generated and saved.")
        points_templates = get_templates(niche) # Reload
        points_templates = [t for t in points_templates if t['pain_point_id'] == target_pain['id']]

    # 4. Select Leads
    leads = get_leads_by_status("new")
    # Filter leads by industry/niche if possible?
    # For now, just take all 'new' leads.
    print(f"\nFound {len(leads)} 'new' leads available for outreach.")
    
    if not send:
        print("Dry run complete. Use --send to actually email.")
        return

    # 5. Send
    if auto:
        print(f"\n[Auto] Confirming send to {len(leads)} leads.")
        confirm = 'YES'
    else:
        confirm = input(f"About to send to {len(leads)} leads. Type 'YES' to confirm: ")
        
    if confirm != 'YES':
        print("Aborted.")
        return

    mailer = Mailer()
    tracking_domain = "http://localhost:5000" # In prod, this is your public IP/Domain
    
    print("\nSending...")
    sent_count = 0
    
    # Use the 'intro' email
    intro_template = next((t for t in points_templates if "intro" in t.get('stage', 'intro') or t['subject']), points_templates[0])
    
    for lead in leads:
        # Personalize
        # Note: We need business_name, contact_person etc. from DB.
        # current get_leads_by_status only returns url/email. 
        # For full personalization we'd fetch full row.
        
        # Inject Tracking Pixel
        tracking_id = f"{lead['email']}:{intro_template['id']}"
        pixel_url = f"{tracking_domain}/open/{tracking_id}"
        pixel_html = f'<img src="{pixel_url}" width="1" height="1" style="display:none;" />'
        
        body = intro_template['body'] + pixel_html
        
        # Send
        if mailer.send_email(lead['email'], intro_template['subject'], body):
            mark_contacted(lead['email'])
            sent_count += 1
            time.sleep(2) # Polite delay
            
    print(f"Sent {sent_count} emails.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("niche", help="Target Industry/Niche")
    parser.add_argument("product", help="Your Product Name")
    parser.add_argument("desc", help="Product Description")
    parser.add_argument("--send", action="store_true", help="Actually send emails")
    parser.add_argument("--auto", action="store_true", help="Auto-select and auto-confirm")
    args = parser.parse_args()
    
    run_campaign(args.niche, args.product, args.desc, args.send, args.auto)
