import csv
import os
import time
import json
import requests
import argparse
from typing import List, Dict, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def get_page_content(url: str, timeout: int = 15) -> Optional[str]:
    """
    Fetches the homepage content of a URL.
    Returns trimmed text content or None if failed.
    """
    if not url.startswith('http'):
        url = 'https://' + url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Get visible text
        text = soup.get_text(separator=' ', strip=True)
        
        # Limit text length to avoid token limits (approx 20k chars is plenty for homepage analysis)
        return text[:20000]
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def analyze_with_gemini(text: str) -> Dict:
    """
    Sends text to Gemini API for analysis.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    prompt = """
    Analyze the following website content for a business. 
    Return a JSON object with strictly these keys:
    {
        "industry": "Primary industry (e.g. Software, Construction, Retail, Interior Design)",
        "business_type": "B2B, B2C, or Hybrid",
        "summary": "A concise one-sentence summary of what the business does/offers.",
        "confidence": 0.0 to 1.0 (float) indicating your confidence in this assessment based on the text.
    }
    
    IMPORTANT: Return ONLY the JSON object. Do not wrap it in markdown block.
    
    If the text is empty, irrelevant, or looks like a parked domain/error page, set confidence to 0.0 and summary to "Invalid or inaccessible content".
    
    Website Content:
    """ + text[:10000] # Truncate again to be safe

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        content_text = result['candidates'][0]['content']['parts'][0]['text']
        # Clean up code blocks if present
        content_text = content_text.replace('```json', '').replace('```', '').strip()
        return json.loads(content_text)
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"API Response Body: {response.text}")
        return {
            "industry": "Unknown",
            "business_type": "Unknown",
            "summary": f"Analysis failed: {str(e)}",
            "confidence": 0.0
        }

def process_csv(input_file: str, output_file: str):
    """
    Reads input CSV, processes each row, and writes to output CSV.
    Expects input CSV to have 'email' or 'website' column.
    """
    rows = []
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        # Normalize headers (strip whitespace)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Determine target column
    target_col = None
    if 'website' in fieldnames:
        target_col = 'website'
    elif 'email' in fieldnames:
        target_col = 'email'
    else:
        print("Error: Input CSV must contain 'website' or 'email' column.")
        return

    # Add new columns
    new_fields = ['ai_industry', 'ai_business_type', 'ai_summary', 'ai_confidence']
    output_fieldnames = fieldnames + new_fields
    
    print(f"Processing {len(rows)} rows from {input_file}...")
    
    processed_rows = []
    
    for i, row in enumerate(rows):
        target_val = row.get(target_col, '').strip()
        
        url = None
        if target_col == 'email':
            if '@' in target_val:
                domain = target_val.split('@')[-1]
                if domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                    url = domain
        else:
            url = target_val
            
        print(f"[{i+1}/{len(rows)}] Analyzing: {url if url else 'Skipped (No valid URL)'}")
        
        ai_result = {k: '' for k in new_fields} # Default empty
        
        if url:
            content = get_page_content(url)
            if content and len(content) > 100:
                # Add delay to avoid rate limits if necessary
                time.sleep(1) 
                analysis = analyze_with_gemini(content)
                ai_result['ai_industry'] = analysis.get('industry', 'Unknown')
                ai_result['ai_business_type'] = analysis.get('business_type', 'Unknown')
                ai_result['ai_summary'] = analysis.get('summary', '')
                ai_result['ai_confidence'] = analysis.get('confidence', 0.0)
            else:
                ai_result['ai_summary'] = "Could not scrape content"
        
        row.update(ai_result)
        processed_rows.append(row)
        
        # Save progress every 10 rows
        if (i + 1) % 10 == 0:
            write_csv(output_file, output_fieldnames, processed_rows)

    # Final save
    write_csv(output_file, output_fieldnames, processed_rows)
    print(f"\nDone! Results saved to {output_file}")

def write_csv(filename, fieldnames, rows):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze business leads using Gemini AI.")
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("--output", "-o", help="Path to output CSV file (optional)")
    
    args = parser.parse_args()
    
    input_path = args.input_csv
    output_path = args.output
    
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_analyzed{ext}"
        
    process_csv(input_path, output_path)
