import sqlite3
import pandas as pd
import json

def generate_report():
    conn = sqlite3.connect('leads.db')
    # Get the last search source
    c = conn.cursor()
    c.execute("SELECT source FROM leads ORDER BY created_at DESC LIMIT 1")
    last_source = c.fetchone()[0]
    
    query = f"SELECT * FROM leads WHERE source = '{last_source}' ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()

    total_leads = len(df)
    unique_domains = df['url'].apply(lambda x: x.split('//')[-1].split('/')[0] if x else 'Unknown').nunique()
    leads_with_email = df[df['email'].notnull() & (df['email'] != '')].shape[0]
    leads_with_phone = df[df['phone_number'].notnull() & (df['phone_number'] != 'Unknown')].shape[0]
    
    # Representative companies
    companies = df[df['company_name'].notnull() & (df['company_name'] != 'None')]['company_name'].unique()[:10]
    
    report = {
        "search_query": last_source,
        "total_leads": total_leads,
        "unique_businesses": unique_domains,
        "leads_with_email": leads_with_email,
        "leads_with_phone": leads_with_phone,
        "sample_companies": companies.tolist()
    }
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print(json.dumps(report, indent=2))
