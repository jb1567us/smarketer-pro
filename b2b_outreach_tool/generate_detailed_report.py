import sqlite3
import pandas as pd
from urllib.parse import urlparse

def get_company_name_from_domain(url):
    if not url:
        return "Unknown"
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    name = domain.split('.')[0]
    return name.capitalize()

def generate_detailed_csv():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    c.execute("SELECT source FROM leads ORDER BY created_at DESC LIMIT 1")
    last_source = c.fetchone()[0]
    
    query = f"SELECT url, email, industry, qualification_score, relevance_reason FROM leads WHERE source = '{last_source}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['company_name'] = df['url'].apply(get_company_name_from_domain)
    
    # Sort by domain richness (e.g. unique domains first)
    df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc if x else 'Unknown')
    summary_df = df.sort_values('domain').drop_duplicates('domain')
    
    output_file = f"parsed_results_{int(pd.Timestamp.now().timestamp())}.csv"
    summary_df.to_csv(output_file, index=False)
    return output_file, summary_df.head(20).to_dict('records'), len(summary_df), last_source

if __name__ == "__main__":
    file_path, top_leads, count, source = generate_detailed_csv()
    print(f"File created: {file_path}")
    print(f"Total unique companies: {count}")
    print(f"Source: {source}")
    print("Top 20 leads:")
    for lead in top_leads:
        print(f"- {lead['company_name']} ({lead['email']})")
