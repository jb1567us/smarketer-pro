import sys
import os
import time
import random
import csv

# Ensure the current directory is in path or import relatively
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import search_searxng
from extractor import extract_emails_from_url
from mailer import Mailer, get_article_template

def main(keywords):
    print(f"Starting Outreach Workflow for keywords: {keywords}")
    
    # 1. Scrape URLs
    # Using SearXNG for reliable results
    urls = search_searxng(keywords, num_results=20)
    
    if not urls:
        print("No URLs found. Exiting.")
        return

    # 2. Extract Emails
    leads = [] # List of dicts: {'url': url, 'emails': [list]}
    
    for url in urls:
        print(f"Processing {url}...")
        emails = extract_emails_from_url(url)
        if emails:
            print(f"  Found emails: {emails}")
            leads.append({'url': url, 'emails': list(emails)})
        
        # Be polite to servers
        time.sleep(random.uniform(1, 3))

    if not leads:
        print("No emails extracted.")
        return

    # Save leads to CSV
    timestamp = int(time.time())
    filename = f"leads_{timestamp}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Emails'])
        for lead in leads:
            writer.writerow([lead['url'], ",".join(lead['emails'])])
    
    print(f"Leads saved to {filename}")

    # 3. Send Emails (Optional / Requires Config)
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if not smtp_user or not smtp_pass:
        print("\nWARNING: SMTP credentials not set. Skipping email sending.")
        print("To send emails, set SMTP_USER and SMTP_PASS environment variables.")
        return

    # Assuming Gmail for default
    mailer = Mailer("smtp.gmail.com", 587, smtp_user, smtp_pass, smtp_user)
    
    print("\nSending emails...")
    for lead in leads:
        for email in lead['emails']:
            # Personalization could go here if we extracted names
            subject = "Article: Optimizing your workflow"
            content = get_article_template()
            
            success = mailer.send_email(email, subject, content)
            if success:
                # Wait between emails to avoid spam filters
                time.sleep(random.uniform(10, 30))
            else:
                print("Skipping remaining emails for this batch due to error or limit.")
                return

    print("Workflow completed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter search query (e.g., 'marketing agencies in london'): ")
    
    main(query)
