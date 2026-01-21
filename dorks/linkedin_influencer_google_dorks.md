# Google Dorks for Finding LinkedIn Influencers + Link-in-Bio Pages

These search strings help you find **public LinkedIn creator/influencer profiles** in specific niches, then locate their **off-platform links** (Linktree-style or personal sites).  
Replace placeholders like `{NICHE}`, `{CITY}`, `{AUDIENCE}`, `{PRODUCT}` with your terms.

> LinkedIn is more “professional” than IG/TikTok, so keywords like **speaker**, **consultant**, **newsletter**, **creator**, **coach**, and **founder** work well.

---

## Core “noise filters” (focus on people profiles)

LinkedIn has many non-profile pages (jobs, posts, pulse, learning). This block targets personal profiles:

```text
site:linkedin.com/in -inurl:jobs -inurl:learning -inurl:pulse -inurl:feed -inurl:posts
```

**Notes**
- Personal profiles typically live at `linkedin.com/in/…`
- Company pages are usually `linkedin.com/company/…` (useful for B2B, but not influencers).

---

## 1) Find LinkedIn influencer/creator *profiles* by niche

### Niche + city
```text
site:linkedin.com/in -inurl:jobs -inurl:learning "{NICHE}" "{CITY}" (creator OR "content creator" OR influencer OR speaker OR consultant)
```

### Niche + “creator signals”
```text
site:linkedin.com/in -inurl:jobs -inurl:learning "{NICHE}" ("newsletter" OR "creator" OR "thought leader" OR "public speaker" OR "keynote")
```

### Niche + partnership/contact signals
```text
site:linkedin.com/in -inurl:jobs -inurl:learning "{NICHE}" (partnerships OR sponsorship OR "brand" OR "work with" OR booking OR email OR "media kit")
```

### Audience + niche (tight targeting)
```text
site:linkedin.com/in -inurl:jobs -inurl:learning "{NICHE}" ("for {AUDIENCE}" OR "{AUDIENCE}") (speaker OR consultant OR coach OR creator)
```

---

## 2) Find profiles that *definitely* include Linktree / link-in-bio services

LinkedIn profiles often list external sites; search for common link-in-bio domains:

```text
site:linkedin.com/in ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to" OR "stan.store" OR "carrd.co")
```

Add a niche (optional):

```text
site:linkedin.com/in "{NICHE}" ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to" OR "stan.store" OR "carrd.co")
```

---

## 3) Reverse-search: start from link-in-bio pages, then click through to LinkedIn

```text
site:linktr.ee "{NICHE}" "{CITY}" linkedin
```

```text
site:beacons.ai "{NICHE}" "{CITY}" linkedin
```

```text
site:campsite.bio "{NICHE}" "{CITY}" linkedin
```

```text
site:taplink.cc "{NICHE}" "{CITY}" linkedin
```

```text
site:solo.to "{NICHE}" "{CITY}" linkedin
```

---

## 4) If you already have a name, find their LinkedIn + links fast

### Find LinkedIn profile
```text
"{FULL_NAME}" "{NICHE}" site:linkedin.com/in
```

### Find their link-in-bio
```text
"{FULL_NAME}" (site:linktr.ee OR site:beacons.ai OR site:campsite.bio OR site:taplink.cc OR site:taplink.at OR site:solo.to OR site:stan.store OR site:flow.page OR site:carrd.co)
```

---

## 5) Niche + “deal-ready” signals on LinkedIn

```text
site:linkedin.com/in "{NICHE}" ("open to partnerships" OR "brand partnerships" OR sponsored OR affiliate OR "speaker" OR "book me")
```

---

## 6) Copy/paste “link-in-bio domain pack”

```text
("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink.cc" OR "taplink.at" OR "bio.site" OR "lnk.bio" OR "direct.me" OR "flow.page" OR "stan.store" OR "solo.to" OR "carrd.co")
```

---

## Quick workflow

1. Use Section 1 to find profiles in your niche (add `{CITY}` for local creators).
2. Use Section 5 to find people explicitly open to partnerships/speaking/affiliate work.
3. Use Section 2 to confirm they list external links or link-in-bio services.
4. Use Section 3 to discover more creators via link-in-bio pages.

---

## Example fill-ins

- `{NICHE}`: `marketing`, `cybersecurity`, `real estate`, `leadership`, `SaaS`, `recruiting`, `AI`
- `{CITY}`: `Austin`, `Dallas`, `Chicago`, `New York`
- `{AUDIENCE}`: `founders`, `sales teams`, `job seekers`, `small business owners`
