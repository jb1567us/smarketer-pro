# Google Dorks for Finding Twitter/X Influencers + Link-in-Bio Pages

These search strings help you find **public Twitter/X profile pages** in specific niches, then locate their **link-in-bio** pages (Linktree-style).  
Replace placeholders like `{NICHE}`, `{CITY}`, `{AUDIENCE}`, `{PRODUCT}` with your terms.

---

## Core “noise filters” (focus on profile pages)

Twitter/X results often include posts (`/status/`) instead of profiles. Use these filters:

### For X (x.com)
```text
site:x.com -inurl:/status/ -inurl:/i/ -inurl:/hashtag -inurl:/search
```

### For legacy Twitter (twitter.com) fallback
```text
site:twitter.com -inurl:/status/ -inurl:/i/ -inurl:/hashtag -inurl:/search
```

**Tip:** If one domain is thin, run the same query with the other.

---

## 1) Find influencer *profiles* by niche

### Niche + city
```text
site:x.com -inurl:/status/ -inurl:/i/ "{NICHE}" "{CITY}" (creator OR influencer OR newsletter OR podcast)
```

### Niche + “collab signals”
```text
site:x.com -inurl:/status/ -inurl:/i/ "{NICHE}" ("DM for collabs" OR collabs OR sponsorship OR "brand deals" OR "work with" OR "paid partnership")
```

### Niche + business/contact signals
```text
site:x.com -inurl:/status/ -inurl:/i/ "{NICHE}" (email OR booking OR inquiries OR "media kit" OR "rate card")
```

### Audience + niche (tight targeting)
```text
site:x.com -inurl:/status/ -inurl:/i/ "{NICHE}" ("for {AUDIENCE}" OR "{AUDIENCE}") (email OR collabs OR sponsorship)
```

> Run the same patterns on `site:twitter.com` if needed.

---

## 2) Find creators who *definitely* have a Linktree / link-in-bio

Search profiles for common link-in-bio domains:

```text
site:x.com -inurl:/status/ -inurl:/i/ ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to" OR "stan.store")
```

Add a niche (optional):

```text
site:x.com -inurl:/status/ -inurl:/i/ "{NICHE}" ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to" OR "stan.store")
```

---

## 3) Reverse-search: start from link-in-bio pages, then click through to X/Twitter

```text
site:linktr.ee "{NICHE}" "{CITY}" (x.com OR twitter)
```

```text
site:beacons.ai "{NICHE}" "{CITY}" (x.com OR twitter)
```

```text
site:campsite.bio "{NICHE}" "{CITY}" (x.com OR twitter)
```

```text
site:taplink.cc "{NICHE}" "{CITY}" (x.com OR twitter)
```

---

## 4) If you already have a handle, find their link-in-bio fast

```text
"{HANDLE}" (site:linktr.ee OR site:beacons.ai OR site:campsite.bio OR site:taplink.cc OR site:taplink.at OR site:solo.to OR site:stan.store OR site:flow.page OR site:carrd.co)
```

---

## 5) Niche + “deal-ready” signals

```text
site:x.com -inurl:/status/ -inurl:/i/ "{NICHE}" (sponsored OR affiliate OR "discount code" OR "promo code" OR ambassador)
```

---

## 6) Copy/paste “link-in-bio domain pack”

```text
("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink.cc" OR "taplink.at" OR "bio.site" OR "lnk.bio" OR "direct.me" OR "flow.page" OR "stan.store" OR "solo.to" OR "carrd.co")
```

---

## Quick workflow

1. Use Section 1 to find niche profiles (add `{CITY}` if you want local).
2. Use Section 5 to find creators already doing sponsored/affiliate posts.
3. Use Section 2 to confirm link-in-bio.
4. Use Section 3 to discover more creators from link-in-bio pages.

---

## Example fill-ins

- `{NICHE}`: `fitness`, `crypto`, `marketing`, `skincare`, `travel`, `AI`, `dog training`
- `{CITY}`: `Austin`, `New York`, `Chicago`, `Los Angeles`
- `{AUDIENCE}`: `founders`, `new moms`, `students`, `runners`
