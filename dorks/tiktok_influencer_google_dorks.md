# Google Dorks for Finding TikTok Influencers + Link-in-Bio Pages

These search strings help you find **public TikTok creator profile pages** in specific niches, and then locate their **link-in-bio** pages (Linktree-style).  
Replace placeholders like `{NICHE}`, `{CITY}`, `{PRODUCT}`, `{AUDIENCE}` with your terms.

---

## Core “noise filters” (focus on TikTok profile pages)

TikTok search results can include tags, videos, sounds, and discovery pages. This block helps reduce noise:

```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ -inurl:/discover -inurl:/search
```

**Notes**
- TikTok profiles usually include `@` in the URL (e.g., `/@username`), so `inurl:/@` is the big win.
- If you’re missing results, temporarily remove some `-inurl:` filters.

---

## 1) Find TikTok creator *profiles* by niche

### Niche + city
```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" "{CITY}" (creator OR influencer OR "content creator")
```

### Niche + “collab signals”
```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" ("collab" OR "brand deals" OR "paid partnership" OR "work with" OR "PR package")
```

### Niche + business/contact signals
```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" ("email" OR booking OR inquiries OR "media kit" OR "rate card")
```

### Audience + niche (tight targeting)
```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" ("for {AUDIENCE}" OR "{AUDIENCE}") ("email" OR booking OR collab OR partnerships)
```

---

## 2) Find creators who *definitely* have a Linktree / link-in-bio

Search TikTok profile pages for common link-in-bio domains:

```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to")
```

### Add city (optional)
```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" "{CITY}" ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to")
```

---

## 3) Reverse-search: start from link-in-bio pages, then click through to TikTok

Often cleaner than starting from TikTok:

```text
site:linktr.ee "{NICHE}" "{CITY}" tiktok
```

```text
site:beacons.ai "{NICHE}" "{CITY}" tiktok
```

```text
site:campsite.bio "{NICHE}" "{CITY}" tiktok
```

```text
site:taplink.cc "{NICHE}" "{CITY}" tiktok
```

```text
site:solo.to "{NICHE}" "{CITY}" tiktok
```

---

## 4) If you already have a TikTok username, locate their link-in-bio fast

```text
"{USERNAME}" (site:linktr.ee OR site:beacons.ai OR site:campsite.bio OR site:taplink.cc OR site:taplink.at OR site:solo.to OR site:stan.store OR site:flow.page OR site:carrd.co)
```

Also try pairing the username with “tiktok” (helpful for common names):

```text
"{USERNAME}" tiktok (site:linktr.ee OR site:beacons.ai OR site:campsite.bio OR site:taplink.cc OR site:solo.to)
```

---

## 5) Niche + “deal-ready” creator signals

These keywords often correlate with creators open to brand deals:

```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" ("ugc" OR sponsored OR affiliate OR ambassador OR "discount code")
```

```text
site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ "{NICHE}" ("amazon storefront" OR LTK OR "shop my" OR "link in bio")
```

---

## 6) Copy/paste “link-in-bio domain pack”

Use this inside other queries:

```text
("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink.cc" OR "taplink.at" OR "bio.site" OR "lnk.bio" OR "direct.me" OR "flow.page" OR "stan.store" OR "solo.to" OR "carrd.co")
```

---

## Quick workflow (fast + practical)

1. **Find profiles** for a niche using Section 1 queries (start with `{NICHE}` + `{CITY}` if you want locals).
2. **Filter to collab-ready** using Section 5 queries (UGC / sponsored / affiliate / media kit).
3. **Confirm link-in-bio** using Section 2 queries.
4. **Reverse-search link pages** (Section 3) to find more creators in the same niche.
5. Build a shortlist and verify: recent posting, consistent niche, engagement quality, and clear contact/links.

---

## Example fill-ins

- `{NICHE}`: `fitness`, `hair stylist`, `texas bbq`, `skincare`, `plant mom`, `travel`, `streetwear`, `real estate`
- `{CITY}`: `Austin`, `Dallas`, `Chicago`, `Denver`
- `{AUDIENCE}`: `new moms`, `college students`, `runners`, `small business owners`
