import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.abspath("src"))

from extractor import detect_tech_stack
from database import add_lead, init_db, get_connection
from mailer import Mailer

def test_tech_stack_detection():
    print("Testing Tech Stack Detection...")
    sample_html = """
    <html>
        <head>
            <meta name="generator" content="WordPress 6.0" />
            <link rel='stylesheet' id='wp-block-library-css' href='https://example.com/wp-includes/css/dist/block-library/style.min.css' media='all' />
            <script src="https://cdn.shopify.com/s/files/1/0000/0000/t/1/assets/theme.js"></script>
        </head>
        <body>
            <div id="__next"></div>
            <script>var __NEXT_DATA__ = {props:{pageProps:{}}};</script>
        </body>
    </html>
    """
    stack = detect_tech_stack(sample_html)
    print(f"Detected Stack: {stack}")
    
    expected = ['WordPress', 'Shopify', 'Next.js']
    missing = [t for t in expected if t not in stack]
    if missing:
        print(f"FAILED: Missing {missing}")
    else:
        print("PASSED: Tech Stack Detection")

def test_database_update():
    print("\nTesting Database Schema and Insertion...")
    init_db() # Should migrate
    
    # Try adding a lead with tech stack
    success = add_lead(
        "https://test-tech-stack.com", 
        "test@techstack.com", 
        tech_stack="WordPress, Shopify"
    )
    
    if success:
        print("Lead added successfully.")
        # Verify it saved
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT tech_stack FROM leads WHERE email='test@techstack.com'")
        row = c.fetchone()
        conn.close()
        
        if row and row[0] == "WordPress, Shopify":
            print(f"PASSED: Database save and retrieve verified. Value: {row[0]}")
        else:
            print(f"FAILED: Database value mismatch. Got: {row}")
    else:
        print("Lead already exists (or failed), skipping insertion test.")

def test_mailer_init():
    print("\nTesting Mailer Initialization...")
    try:
        m = Mailer()
        print("PASSED: Mailer initialized (providers loaded).")
    except Exception as e:
        print(f"FAILED: Mailer init error: {e}")

if __name__ == "__main__":
    test_tech_stack_detection()
    test_database_update()
    test_mailer_init()
