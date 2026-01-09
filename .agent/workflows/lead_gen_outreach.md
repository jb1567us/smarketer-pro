---
description: Automated B2B Lead Generation and Outreach Campaign
---

# B2B Lead Generation & Outreach Workflow

This workflow automates the process of finding leads, qualifying them, enriching their data, and saving them to the CRM.

## Prerequisites

- [x] Proxies gathered (Auto-handled by Proxy Manager)
- [x] LLM API Keys configured in `.env`

## Steps

### 1. Run the Outreach Agent

Execute the main workflow script with your target keywords and niche.

```bash
# Syntax: python src/workflow.py [keywords...] --niche "Target Industry" --profile "Lead Category"
# Example:
python src/workflow.py "SaaS Founders" "CTO" --niche "Tech Startups" --profile "Q3_Cold_Outreach"
```

### 2. Monitor Progress

The script will:

1. **Search**: Use `ResearcherAgent` to find candidate URLs.
2. **Filter**: Apply exclusion lists.
3. **Analyze**: Run `ResearcherAgent` (Deep Scrape) and `QualifierAgent` (ICP Check) on each site.
4. **Save**: Qualified leads are saved to `leads.db`.

### 3. Review Leads in CRM

1. Open the App: `streamlit run src/app.py`
2. Navigate to **Lead Gen > Lead Discovery**.
3. Filter by the Category you used (e.g., "Q3_Cold_Outreach").

### 4. Launch Campaign from UI

1. Navigate to **Marketing > Campaigns**.
2. Click **"Create New Campaign"**.
3. Select the leads you just harvested.
4. Configure the `CopywriterAgent` to generate sequences.
5. Start the campaign.
