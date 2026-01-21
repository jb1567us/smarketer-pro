# Google Dorks for Finding Instagram Influencers + Link-in-Bio Pages

These search strings help you find **public** Instagram influencer/profile pages in specific niches, and then locate their **link-in-bio** pages (Linktree-style).  
Replace placeholders like `{NICHE}`, `{CITY}`, `{PRODUCT}`, `{AUDIENCE}` with your terms.

---

## Core “noise filters” (use these to focus on profile pages)

Instagram has lots of non-profile URLs (tags, posts, reels, explore). This block helps reduce that:

```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel
```

You can append that to most searches below.

---

## 1) Find influencer *profiles* by niche

### Niche + city
```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" "{CITY}" ("ugc" OR "content creator" OR influencer OR creator)
```

### Niche + “collab signals”
```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" ("DM for collabs" OR collabs OR "brand ambassador" OR PR OR gifted)
```

### Niche + business signals (email/booking)
```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" ("email" OR booking OR inquiries OR "media kit" OR "rate card")
```

### Audience + niche (tight targeting)
```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" ("for {AUDIENCE}" OR "{AUDIENCE}") ("email" OR booking OR collabs)
```

---

## 2) Find influencers who *definitely* have a Linktree / link-in-bio

Search Instagram profile pages for common link-in-bio domains:

```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink")
```

### Add city (optional)
```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" "{CITY}" ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink")
```

---

## 3) Reverse-search: start from Link-in-bio pages, then click through to Instagram

Often cleaner than starting from Instagram:

```text
site:linktr.ee "{NICHE}" "{CITY}" instagram
```

```text
site:beacons.ai "{NICHE}" "{CITY}" instagram
```

```text
site:campsite.bio "{NICHE}" "{CITY}" instagram
```

```text
site:taplink.cc "{NICHE}" "{CITY}" instagram
```

(Depending on the service, you may also try `site:taplink.at ...`.)

---

## 4) If you already have a username, locate their link-in-bio fast

```text
"{USERNAME}" (site:linktr.ee OR site:beacons.ai OR site:campsite.bio OR site:taplink.cc OR site:taplink.at)
```

You can broaden the “link-in-bio” net:

```text
"{USERNAME}" ("link in bio" OR "links" OR "shop my" OR "my links") (site:linktr.ee OR site:beacons.ai OR site:campsite.bio OR site:taplink.cc OR site:taplink.at OR site:bio.site OR site:lnk.bio OR site:direct.me OR site:flow.page OR site:stan.store OR site:solo.to OR site:carrd.co)
```

---

## 5) Niche + “deal-ready” creator signals

These keywords often correlate with creators open to brand deals:

```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" ("ugc" OR "paid partnership" OR sponsored OR "brand deal" OR affiliate OR ambassador)
```

```text
site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel "{NICHE}" ("amazon storefront" OR "LTK" OR "shop my" OR "discount code")
```

---

## 6) Copy/paste “link-in-bio domain pack”

Use this inside other queries:

```text
("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink.cc" OR "taplink.at" OR "bio.site" OR "lnk.bio" OR "direct.me" OR "flow.page" OR "stan.store" OR "solo.to" OR "carrd.co")
```

---

## Quick workflow (fast + practical)

1. **Find profiles** for a niche using Section 1 queries.  
2. **Filter to collab-ready** using Section 5 queries (UGC / media kit / booking).  
3. **Confirm link-in-bio** using Section 2 queries.  
4. **Reverse-search link pages** (Section 3) to find more creators in the same niche.  
5. Build a short list and check for: recent posts, consistent content, clear niche, and contact options.

---

## Example fill-ins

- `{NICHE}`: `fitness`, `hair stylist`, `texas bbq`, `skincare`, `plant mom`, `travel`, `streetwear`
- `{CITY}`: `Austin`, `Dallas`, `Chicago`, `Denver`
- `{AUDIENCE}`: `new moms`, `college students`, `runners`, `small business owners`

