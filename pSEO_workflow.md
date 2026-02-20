# pSEO Workflow: Database-Driven Authority Sites

This document outlines the standard operating procedure (SOP) for generating high-quality, database-driven content for the Site Factory. It prioritizes "Helpful Content" (HCU) compliance by placing user intent and unique value-adds before scale.

## The 8-Step Pipeline

### Step 1: Define the ICP (Who)
**Goal:** Define the searcher with a "Job to be Done" (JTBD) before touching data.
*   **Searcher Persona:** (e.g., Beginner in a hurry vs. Expert researcher)
*   **Job-to-be-Done:** (e.g., Troubleshoot urgency vs. Compare prices)
*   **Trust Needs:** (e.g., Citations, Last Updated, Safety Disclaimers)
*   **Conversion Tolerance:** (e.g., High for commercial, Low for info)
*   **Output:** `ICP_Brief.json`

### Step 2: Intent Mapping (What)
**Goal:** Map specific keywords to "Intent Clusters" rather than broad topics.
*   **Commercial Investigation:** "best", "vs", "review"
*   **Transactional:** "buy", "price", "coupon"
*   **Lead Intent:** "service", "quote", "near me"
*   **Info (Support):** "how to", "checklist"
*   **Output:** `Keyword_Map.json`

### Step 3: SERP Reality Check (Why Us)
**Goal:** Validate if we can beat existing results.
*   **Competitor Type:** Directories vs. Editorial vs. Forums?
*   **Gap Analysis:** Do we need better data, better UX, or better authority?
*   **Avoid:** Queries heavily answered by AI Summaries/Snippets.

### Step 4: Data Inventory (The Raw Material)
**Goal:** Select datasets that support the *better answer*.
*   **Scoring Criteria:**
    *   Uniqueness (Commodity vs. Rare)
    *   Coverage (Scale potential)
    *   Join Potential (Can we enrich relative to competitors?)
*   **Output:** `Data_Inventory.json`

### Step 5: Design the "Value-Add" (The HCU Factor)
**Goal:** Define purely unique modules that prevent "Thin Content".
*   **A) Compute:** Scores, rankings, indices, comparisons.
*   **B) Explain:** AI generated interpretation specific to the record.
*   **C) Discovery:** Related items graph (not random).
*   **D) Trust:** Citations, authorship, transparency.
*   **Output:** `Value_Add_Spec.json`

### Step 6: Page Types & Indexing (Safety)
**Goal:** Prevent index bloat.
*   **Types:** Hubs, Detail Pages (only high quality), Comparisons, Collections.
*   **Rule:** `noindex` thin pages, infinite facets, or low-demand variants.

### Step 7: Monetization Alignment
**Goal:** Match monetization to intent.
*   **Investigation:** Affiliate / Comparison.
*   **Info:** Email / Lead Magnet.
*   **Local:** Lead Gen / Quotes.

### Step 8: Publish & Feedback Loop
*   Launch batch (200-1k pages).
*   Measure: Indexation rate, CTR, Conversion.
*   Scale winners.

---

## Go/No-Go Scoring Rubric (Must be >18/25)
1.  **Demand Quality (1-5):** Real intent?
2.  **Dataset Advantage (1-5):** Hard to copy?
3.  **Value-Add Strength (1-5):** Better than SERP?
4.  **Monetization Fit (1-5):** Natural conversion?
5.  **SEO Safety (1-5):** Avoids thin content?

---

## Example: Hiking Safety
*   **ICP:** Beginners/Families.
*   **Intent:** "Best boots", "Safety checklist".
*   **Data:** Trails + Weather + Incidents.
*   **Value-Add:** "Safety Score", "Live Conditions".
*   **Monetization:** Gear Affiliate + Email Pack.
