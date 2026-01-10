---
description: Advanced SEO Link Wheel Construction
---

# SEO Link Wheel Builder

Automate the creation of tiered backlink structures (Link Wheels) to boost ranking.

## Steps

### 1. Launch the Application

```bash
streamlit run src/app.py
```

### 2. Access Link Wheel Builder

Navigate to **SEO & Growth > Link Wheel Builder**.

### 3. Configure the Wheel

1. **Target URL**: The money site you want to rank.
2. **Keywords**: Main keywords to target.
3. **Tier Structure**: Select "Tier 1 (Direct)" or "Tier 2 (Buffer)".
4. **Nodes**: Choose how many Web 2.0 properties (spokes) to create (e.g., 5).

### 4. Generate Content

- The `SEOExpertAgent` will plan the anchor text distribution.
- The `CopywriterAgent` will generate unique, spin-ready articles for each node.

### 5. Automated Posting (WordPress)

- Ensure you have **WordPress Sites** configured in **Settings**.
- Select the sites to use as spokes.
- Click **"Build Wheel"**.
- The `WordPressAgent` will post the content with interlinks to the next spoke and the Target URL.

### 6. Verification

- Use **SEO Audit** to verify the backlinks are live and indexed.
