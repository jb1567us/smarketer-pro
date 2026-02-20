# The 3-Pillar Portfolio Strategy

This document defines the ecosystem architecture, ensuring the **MySQL Database Content Layer** is positioned correctly alongside the DSR and Authority strategies.

## The Ecosystem Triad

### 1. The DSR Site (The "Offer" Engine)

* **Role:** Conversion & Monetization.
* **Focus:** High-intent, specific solutions (e.g., "Book a Consultation", "Buy Service").
* **Traffic Source:** Fed by the high-volume traffic from Pillar 3 and the trust from Pillar 2.
* **Key Metric:** Conversion Rate (CVR).

### 2. The Authority Site (The "Trust" Engine)

* **Role:** Brand & Educational Moat.
* **Strategy (MVA to Library):** Starts as a Minimum Viable Asset (niche expert) and expands into a comprehensive library.
* **Focus:** Deep, editorial content, high E-E-A-T (Experience, Expertise, Authority, Trust).
* **Key Metric:** Backlinks & Brand/Returning Users.

### 3. The Database-Driven Site (The "Traffic" Content Layer)

* **Role:** Scale & Acquisition.
* **Strategy:** Programmatic SEO using the **MySQL Information Layer**.
* **Source:** Powered by data from the "B2B Outreach Tool" (Scraped/Enriched Data).
* **Function:**
  * Captures long-tail, low-volume/high-quantity keywords (e.g., "Best [Niche] in [City]").
  * **The "Feeder":** Interlinks heavily to Pillar 2 (for generic info) and Pillar 1 (for solutions).
* **Key Metric:** Total Indexed Pages & Organic Impressions.

---

## The "Content Layer" Strategy (MySQL Driven)

This pillar is unique because it is **generated**, not written. It leverages your "App" (B2B Outreach Tool) to build the dataset.

### The Pipeline

1. **Harvest (The App):** The B2B Tool scrapes Google Maps/Socials for a niche (e.g., "Roofers").
2. **Enrich (The App):** Adds emails, review counts, social scores.
3. **Store (MySQL):** The structured "Truth" of the industry.
4. **Publish (Site Factory):**
    * **Profile Pages:** "Roofers in Austin: [Company Name] Review".
    * **Comparison Pages:** "Top 10 Roofers in Austin by [Review Count]".
    * **Lead Pages:** "Get a Quote from 5 Austin Roofers".

### Strategic Requirements

To ensure this layer isn't penalized (HCU), it must follow the **pSEO Workflow**:

* **Value Add:** It cannot just be a phone book. It must "compute" something (e.g., a "Reputation Score" based on the raw review data).
* **Interlinking:** It must drive users to the *Authority Site* for "How to hire a roofer" guides (Trust) or the *DSR Site* to "Hire a pro" (Money).
