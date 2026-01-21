# Google Dorks for Finding YouTube Influencers + Link-in-Bio Pages

These search strings help you find **public YouTube channel pages** in specific niches, then locate their **link-in-bio** pages (Linktree-style).  
Replace placeholders like `{NICHE}`, `{CITY}`, `{AUDIENCE}`, `{PRODUCT}` with your terms.

---

## Core “noise filters” (focus on channel pages)

YouTube results often include videos/shorts instead of channels. This block helps focus on channels:

```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) -inurl:/watch -inurl:/shorts -inurl:/results
```

**Notes**
- Modern channels often use `/@handle`.
- If you get too few results, temporarily remove `-inurl:/shorts` or `-inurl:/watch`.

---

## 1) Find YouTube *channels* by niche

### Niche + city
```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) "{NICHE}" "{CITY}" -inurl:/watch -inurl:/shorts
```

### Niche + “creator signals”
```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) "{NICHE}" ("creator" OR "content creator" OR influencer) -inurl:/watch
```

### Niche + sponsorship/contact signals
```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) "{NICHE}" ("business inquiries" OR sponsorship OR "brand deals" OR "work with" OR "media kit" OR "rate card" OR email) -inurl:/watch
```

### Audience + niche (tight targeting)
```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) "{NICHE}" ("for {AUDIENCE}" OR "{AUDIENCE}") ("business inquiries" OR sponsorship OR email) -inurl:/watch
```

---

## 2) Find creators who *definitely* have a Linktree / link-in-bio

Search channel pages for common link-in-bio domains:

```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to" OR "stan.store") -inurl:/watch
```

Add a niche (optional):

```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) "{NICHE}" ("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "solo.to" OR "stan.store") -inurl:/watch
```

---

## 3) Reverse-search: start from link-in-bio pages, then click through to YouTube

Often cleaner than starting from YouTube:

```text
site:linktr.ee "{NICHE}" "{CITY}" youtube
```

```text
site:beacons.ai "{NICHE}" "{CITY}" youtube
```

```text
site:campsite.bio "{NICHE}" "{CITY}" youtube
```

```text
site:taplink.cc "{NICHE}" "{CITY}" youtube
```

```text
site:solo.to "{NICHE}" "{CITY}" youtube
```

---

## 4) If you already have a channel/handle, find their link-in-bio fast

```text
"{CHANNEL_NAME_OR_HANDLE}" (site:linktr.ee OR site:beacons.ai OR site:campsite.bio OR site:taplink.cc OR site:taplink.at OR site:solo.to OR site:stan.store OR site:flow.page OR site:carrd.co)
```

---

## 5) Niche + “deal-ready” signals

```text
site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) "{NICHE}" (sponsored OR affiliate OR "discount code" OR "promo code" OR ambassador) -inurl:/watch
```

---

## 6) Copy/paste “link-in-bio domain pack”

```text
("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink.cc" OR "taplink.at" OR "bio.site" OR "lnk.bio" OR "direct.me" OR "flow.page" OR "stan.store" OR "solo.to" OR "carrd.co")
```

---

## Quick workflow

1. Use Section 1 to find channels in your niche (add `{CITY}` if you want local creators).
2. Use Section 5 to find “deal-ready” creators (sponsored/affiliate signals).
3. Use Section 2 to confirm link-in-bio.
4. Use Section 3 to discover *more* creators from link-in-bio pages.

---

## Example fill-ins

- `{NICHE}`: `fitness`, `texas bbq`, `skincare`, `finance`, `minimalism`, `gaming`, `dog training`
- `{CITY}`: `Austin`, `Dallas`, `Chicago`, `Denver`
- `{AUDIENCE}`: `new moms`, `students`, `runners`, `small business owners`
