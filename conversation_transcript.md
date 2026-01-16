# Conversation Transcript

> Transcript of the user/assistant exchange in this chat (Markdown format).

---

## User
I need an exhaustive list of email providers which offer a free tier with limits. These need to be respected email providers that are not on black lists

## User
i Don't want Yahoo Gmail and those other email providers like that because those things get bounced into spam typically

## User
Let me clarify I wanna find a list of high quality email providers that have a free TIER or free limits and have an API that can be used

## Assistant
Got you — you’re basically looking for **reputable email *sending* providers (ESPs)** (not consumer inboxes like Gmail/Yahoo) that offer a **free tier (or free credits) + an API/SMTP**, and that generally have **solid deliverability reputations** *when used correctly*.

A quick reality-check: **no provider can guarantee “not on blacklists”** forever, because reputation is driven by sender behavior. But the providers below are legitimate, widely used, and have strong anti-abuse programs (which is exactly what you want).

## High-quality email API providers with a free tier (or free credits)

### Forever-free (or free-with-limits) tiers
| Provider | Free tier (what you get) | API/SMTP | Notes |
|---|---:|---|---|
| Postmark | Free “developer” plan: **100 emails/month**, doesn’t expire | API + SMTP | Great transactional deliverability; strict anti-spam. |
| Mailgun | Free plan includes **100 emails/day** | API + SMTP | Strong dev tooling; also strict compliance. |
| Brevo (Sendinblue) | Free plan: **300 emails/day** | API + SMTP | Solid all-in-one (transactional + marketing). |
| Mailjet | Free plan: **6,000 emails/month** (limit **200/day**) | API + SMTP | Established provider; good starter limits. |
| SMTP2GO | Free plan: **1,000 emails/month** (limit **200/day**) | SMTP + API | Simple SMTP relay; popular for “just send the mail.” |
| Resend | Free plan includes an **email API** with a limited monthly/daily quota | API + SMTP | Developer-first; great DX. |
| Mailtrap (Email Sending) | Free plan includes **monthly quota** with a **daily cap** | API + SMTP | Known for testing + sending; good for dev teams. |
| SendPulse | Free plan includes a **monthly sending quota** | API + SMTP | All-in-one style platform; verify your use-case fits their rules. |
| SparkPost (now under Bird/MessageBird ecosystem) | Free “Test” plan: **500 emails/month** and **100/day** | API + SMTP | Free plan details have changed historically—double-check current availability. |

### Free credits / free-for-a-while (still useful)
| Provider | Free tier (what you get) | API/SMTP | Notes |
|---|---:|---|---|
| Amazon SES | **3,000 message charges/month free for 12 months** (AWS Free Tier) | API + SMTP | Best cost later, more setup complexity. |
| SendGrid | Free trial: **100 emails/day for 60 days** | API + SMTP | Big-name ESP, but free is time-limited. |
| Zoho ZeptoMail | “First credit” free: **10,000 transactional emails** | API + SMTP | Great for a one-time free batch to prove out integration. |
| Netcore Email API (Pepipost lineage) | Free plan described as lifetime; **max 1k/day for first month**, then **100/day** | API + SMTP | Confirm current onboarding screens because plans can shift. |

### Smaller/newer (often legit, but “vet carefully”)
| Provider | Free tier | API/SMTP | Notes |
|---|---:|---|---|
| AhaSend | Free tier with limited monthly sends | API + SMTP | Smaller provider; check regional sending + features you need. |
| Maileroo | Free tier with limited monthly sends | API + SMTP | Smaller provider; verify deliverability for your audience. |

### Marketing-first platforms (not ideal for “transactional API” use cases)
| Provider | Free tier | API | Notes |
|---|---:|---|---|
| Klaviyo | Free plan includes **limited monthly email sends** | API | Built for marketing/flows, not as clean for pure transactional patterns. |

## How to avoid “spam folder hell”
- Send from your own domain / subdomain
- Configure SPF + DKIM + DMARC
- Warm up gradually
- Clean lists + unsubscribe for marketing

---

## User
outreach/marketing, i am on a shared provider domain

## User
i have My own domain it's on dedicated hosting on a shared server, which is not good for email sending

## Assistant
You’re thinking about this the right way: **don’t send outreach/marketing from your web host’s shared server IP**. Even if your domain is fine, the *server/IP reputation* is usually what gets you throttled, junk-foldered, or blocklisted.

Below is a **high-quality, “real ESP / email API” list** (not consumer inboxes like Gmail/Yahoo), where you can **bring your own domain**, authenticate it (SPF/DKIM/DMARC), and send via **API and/or SMTP**.

## Best “free tier + API” options (respected providers)

### Marketing/newsletter ESPs (campaign tools + API)
- Brevo (Sendinblue): 300/day + API
- Mailjet: 6,000/month (200/day) + API
- MailerLite: 12,000/month + API
- Sender.net: 15,000/month (verify API availability)
- EmailOctopus: 2,500 subscribers + API
- Zoho Campaigns: 2,000 contacts / 6,000 emails + API
- Benchmark Email: 500 contacts / 3,500 emails + API
- AWeber: 500 subscribers / 3,000 emails + API
- Klaviyo: 250 contacts / 500 emails + API
- SendPulse: free quota + API

### Transactional-first email APIs (watch ToS for cold outreach)
- Mailgun: 100/day + API/SMTP
- Postmark: 100/month + API/SMTP (transactional)
- Resend: 100/day + 3,000/month; marketing limits for contacts
- SMTP2GO: free tier + API
- Amazon SES: free for 12 months (AWS free tier)

## Practical setup suggestion
Use a reputable ESP to send from your domain (with SPF/DKIM/DMARC) instead of your shared server.

---

## User
create a makdown file transcribing all the conversation
