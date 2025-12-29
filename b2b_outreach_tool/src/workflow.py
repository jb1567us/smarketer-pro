import sys
import os
import asyncio
import csv
import time
import aiohttp
import functools

# Appends src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from scraper import search_searxng
from extractor import extract_emails_from_site, fetch_html
from analyzer import analyze_content
from mailer import Mailer, get_email_content
from database import init_db, add_lead, mark_contacted

async def process_url(session, url, target_niche=None):
    """Wrapper to process a single URL: extract emails and analyze content."""
    try:
        # 1. Fetch HTML first (modified extractor to expose fetch or just use extract which does it)
        # To avoid double fetching, we need to inspect extractor.py again or just let it happen.
        # Actually, extract_emails_from_site does fetching internally.
        # Ideally we refactor, but for now let's just use extract and then re-fetch for analysis OR
        # better: just analyze the homepage text if we can get it.
        # Optimization: Let's fetch once here, then pass to extractor?
        # Extractor `extract_emails_from_site` expects session and url.
        
        # New flow:
        # 1. Extract emails (crawls pages)
        emails = await extract_emails_from_site(session, url)
        
        # 2. Analyze (only if we found something OR if we want to filter the lead anyway)
        # Analyzing every site for filtering is better even if no email found (to avoid false negatives? no, if no email, lead is useless)
        # BUT if we want to filter "quality" leads, we must analyze.
        
        analysis = None
        if emails: # Only analyze if we have a way to contact them
             # Fetch homepage text for analysis
             # We need a simple fetch here.
             from extractor import fetch_html
             html = await fetch_html(session, url)
             if html:
                 # Strip HTML tags for cleaner analysis - simple approximation or just pass HTML and let Gemini handle it (it can handle some)
                 # Passing raw HTML is fine for Gemini usually, but text is cheaper token-wise.
                 # For now, pass html text.
                 analysis = analyze_content(html, target_niche)
        
        if analysis and target_niche:
            if not analysis.get('is_relevant', True):
                print(f"Skipping {url}: Not relevant to {target_niche} ({analysis.get('relevance_reason')})")
                return {'url': url, 'emails': [], 'analysis': analysis} # Return empty emails to filter out

        return {'url': url, 'emails': list(emails), 'analysis': analysis}
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return {'url': url, 'emails': []}

async def run_outreach(keywords, profile_name="default", target_niche=None):
    print(f"Starting Outreach Workflow for keywords: {keywords} [Profile: {profile_name}] [Niche: {target_niche}]")
    init_db()
    
    # Load profile settings
    profiles = config["search"].get("profiles", {})
    profile_data = profiles.get(profile_name, profiles.get("default", {}))
    categories = profile_data.get("categories")
    engines = profile_data.get("engines")
    
    async with aiohttp.ClientSession() as session:
        # 1. Search
        urls = await search_searxng(
            keywords, 
            session, 
            num_results=config["search"]["max_results"],
            categories=categories,
            engines=engines
        )
        
        if not urls:
            print("No URLs found. Exiting.")
            return

        # 2. Extract (Concurrent)
        print(f"Processing {len(urls)} URLs concurrently...")
        tasks = [process_url(session, url, target_niche=target_niche) for url in urls]
        # Run in batches if needed, but for <50, gather is fine
        results = await asyncio.gather(*tasks)

    # 3. Process Results & Save to DB
    new_leads = []
    
    for res in results:
        url = res['url']
        emails = res['emails']
        analysis = res.get('analysis') or {}
        
        if emails:
            print(f"[{url}] Found: {emails}")
            for email in emails:
                # Add to DB (returns True if new)
                if add_lead(
                    url, 
                    email, 
                    source=keywords, 
                    category=profile_name,
                    industry=analysis.get('industry'),
                    business_type=analysis.get('business_type'),
                    confidence=analysis.get('confidence'),
                    relevance_reason=analysis.get('relevance_reason'),
                    contact_person=analysis.get('contact_person')
                ):
                    new_leads.append({'url': url, 'email': email, 'analysis': analysis})
        else:
            pass # No emails found
            
    if not new_leads:
        print("No new unique leads found.")
        return

    # 4. Save to CSV (Batch Record)
    timestamp = int(time.time())
    filename = f"leads_{timestamp}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Email', 'Industry', 'Business Type', 'Confidence', 'Relevance Reason', 'Contact Person'])
        for lead in new_leads:
            analysis = lead.get('analysis') or {}
            writer.writerow([
                lead['url'], 
                lead['email'],
                analysis.get('industry', ''),
                analysis.get('business_type', ''),
                analysis.get('confidence', ''),
                analysis.get('relevance_reason', ''),
                analysis.get('contact_person', '')
            ])
    
    print(f"Saved {len(new_leads)} new leads to {filename}")

    # 5. Send Emails
    # Check if enabled
    smtp_user = config["email"]["smtp_user"]
    if not smtp_user:
        print("SMTP config missing. Skipping emails.")
        return

    mailer = Mailer()
    print("\nSending emails...")
    
    for lead in new_leads:
        email = lead['email']
        subject, content = get_email_content() # could pass business name if we had it
        
        success = mailer.send_email(email, subject, content)
        if success:
            mark_contacted(email)
            # Short sleep to be polite to SMTP server even if sync
            time.sleep(1) 
            
    print("Workflow completed.")

if __name__ == "__main__":
    # Fix for Windows Async Loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import argparse
    parser = argparse.ArgumentParser(description="B2B Outreach Tool")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--profile", default="default", help="Search profile (default, tech, creative, news)")
    parser.add_argument("--niche", help="Target niche for AI verification (e.g. 'Interior Design', 'SaaS')")
    
    args = parser.parse_args()
    
    if args.query:
        query = " ".join(args.query)
    else:
         # Default from config or input
        query_list = config["search"]["keywords"]
        if query_list:
            query = query_list[0]
        else:
            query = input("Enter search query: ")
    
    asyncio.run(run_outreach(query, profile_name=args.profile, target_niche=args.niche))
