# Directive: Lead Enrichment (Hybrid Model)

**Goal**: Find contact information for Qualified Leads.
**Priority**: Balance Cost vs. Value.

## Strategy: The Hybrid Loop

1. **Level 1: The "Fast Pass" (Free/Cheap)**
    - Scan Homepage, Contact Page, About Page.
    - Look for `mailto:` links, Phone numbers, Physical Address.
    - *Deep Dive Trigger*: If `Generic Email Found` (info@/contact@) **AND** `High Value Signal` (e.g. Company seems large, >50 employees, public company), -> **GO TO LEVEL 2**.
    - Else -> Save and Done.

2. **Level 2: The "Deep Dive" (Premium)**
    - Use enrichment APIs (e.g. Apollo, Hunter).
    - Target: "Decision Maker" (CEO, Founder, Marketing Director).
    - *Constraint*: Only use if authorized by user settings (Credits cost check).

## Inputs

- `url`: The company website.
- `enrichment_depth`: "shallow" (Level 1 only) or "hybrid" (Level 1 -> Trigger -> Level 2) or "deep" (Always Level 2).

## Execution Tool

- `execution/enrich_lead.py`
