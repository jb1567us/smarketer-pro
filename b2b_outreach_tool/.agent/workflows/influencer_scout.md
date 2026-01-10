---
description: B2C Influencer Scout and Outreach
---

# Influencer Scout Workflow

Find and engage with high-impact influencers for your brand.

## Steps

### 1. Launch the Application

```bash
streamlit run src/app.py
```

### 2. Switch to B2C Mode

1. In the Sidebar, ensure **App Mode** is set to **B2C**.
2. Navigate to **Audience & Growth > Influencer Scout**.

### 3. Scout for Creators

1. Enter your **Niche** (e.g., "Sustainable Fashion").
2. Select **Platform** (Instagram, TikTok, YouTube).
3. Set **Results Limit** (e.g., 10).
4. Click **"🚀 Scout Influencers"**.

### 4. Review & Analyze

- The `InfluencerAgent` will return a list of profiles with follower counts and bio snippets.
- Click **"Analyze"** on a profile to get a deeper report (Engagement rate, Audience demographics - *if API enabled*).

### 5. Outreach

- Click **"Add to CRM"** or **"DM"** to move them to your **Partners** pipeline.
- Use the **Creative Library** to generate a collaboration proposal.
