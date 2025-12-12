# Lead Generation Project - Workspace

## Overview
This workspace contains the complete B2B email lead generation campaign results for interior design firms across 7 countries, with art affinity analysis for targeting abstract art clients.

## Project Structure

```
lead_generation/
├── final_email_lists/          # Ready-to-use email lists (CSV format)
│   ├── EMAILS_GLOBAL_ABSTRACT_FOCUS.csv   # 2,604 emails - Modern/Abstract art focus
│   └── EMAILS_GLOBAL_NEUTRAL.csv          # 6,311 emails - Neutral/unclear focus
│
├── data/                       # Country-specific segmented data
│   ├── ABSTRACT_FOCUS_LEADS_*.csv         # Abstract focus by country
│   └── NEUTRAL_LEADS_*.csv                # Neutral leads by country
│
├── scripts/                    # Utility scripts
│   └── (analysis and processing scripts)
│
└── docs/                       # Documentation
    └── README.md (this file)
```

## Final Results Summary

### Global Email Lists (CSV Format)

**EMAILS_GLOBAL_ABSTRACT_FOCUS.csv** - 2,604 emails
- Firms showing strong affinity for modern/abstract art
- Perfect for pitching abstract artist work
- Columns: `email`, `country`

**Country Breakdown:**
- 🇺🇸 US: 1,853 emails
- 🇩🇪 Germany: 320 emails
- 🇫🇷 France: 128 emails
- 🇪🇸 Spain: 96 emails
- 🇬🇧 UK: 88 emails
- 🇨🇦 Canada: 62 emails
- 🇦🇺 Australia: 57 emails

**EMAILS_GLOBAL_NEUTRAL.csv** - 6,311 emails
- Firms with neutral/unclear art style signals
- Secondary target list
- Columns: `email`, `country`

**Country Breakdown:**
- 🇺🇸 US: 5,141 emails
- 🇩🇪 Germany: 397 emails
- 🇪🇸 Spain: 278 emails
- 🇫🇷 France: 238 emails
- 🇬🇧 UK: 109 emails
- 🇨🇦 Canada: 82 emails
- 🇦🇺 Australia: 66 emails

### Total Verified Designer Emails: 8,915

## Data Quality

All emails have been:
✅ Verified as actual email addresses (not file formats)
✅ Categorized by art style affinity (modern/abstract vs traditional)
✅ Tagged with country of origin
✅ Cleaned of blog/SEO content
✅ Filtered to exclude suppliers (designers only)

## How to Use

### For Email Marketing:
1. Import CSV files into your email marketing platform (Mailchimp, SendGrid, etc.)
2. Use the `country` column to segment campaigns by region
3. Start with the **Abstract Focus** list for highest conversion rates

### For CRM Import:
1. Open CSV in Excel/Google Sheets
2. Map columns: `email` → Email, `country` → Custom Field
3. Import into your CRM system

### For Manual Outreach:
1. Filter by country in the CSV
2. Personalize messages based on art style affinity
3. Reference modern/abstract art in outreach to Abstract Focus list

## Campaign Timeline

- **Data Collection:** Multiple campaigns across 7 countries
- **Art Affinity Analysis:** 6h 47m processing time
- **Final Cleanup:** December 8-9, 2025
- **Total Leads Analyzed:** ~6,800 design firms

## Notes

- All data is current as of December 2025
- Email validation performed via website scraping
- Art affinity scored using multilingual keyword analysis
- Traditional/antique-focused firms excluded from both lists

## Support

For questions about the data or methodology, refer to the original project documentation in the `docs/` folder.
