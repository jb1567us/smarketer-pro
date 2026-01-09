# Project Control Doc

## Objective
- <One sentence, measurable. E.g., "Acquire 500 qualified leads in 60 days at <$15 CPL via LinkedIn + email.">

## Deliverables (artifact registry)
- D1: Campaign Brief v0.1 (owner: AI) ⏳
- D2: ETL Script `etl_leads.py` v0.1 (owner: AI) ⏳
- D3: Tracking Plan (`tracking.yml`) v0.1 (owner: You) ⏳
- D4: Creative Variants (10) v0.1 (owner: AI) ⏳

> Update: After each artifact is produced, increment version, add checksum, and link to file under `/artifacts`.

## Task Graph (DAG)
- T1: Define ICP & channel strategy → D1
- T2: Build/scrape lead ETL → D2
- T3: Map analytics events → D3
- T4: Generate creatives → D4
**Edges:** T1 → (T2, T4); T3 independent

## Interface Contracts (I/O schemas)
- LeadRecord (JSON Schema) v1.0 → `/schemas/leadrecord.schema.json`
- CreativeSpec (JSON Schema) v1.0 → `/schemas/creativespec.schema.json`
- TrackingEvent (JSON Schema) v1.0 → `/schemas/trackingevent.schema.json`

## Decision Log
- {YYYY-MM-DD}: <Decision + rationale>
- {YYYY-MM-DD}: <Decision + rationale>

## Constraints
- Budget: <$$>
- Deadlines: <dates>
- Privacy: <GDPR/CCPA notes>
- Tone/Brand: <voice rules>
- Tech stack: <python 3.11, GA4, Meta/LI, etc.>
- File paths: `/project` root mounted here

## Open Questions
- <Fill in>

---

## Governance Loop (how to use this repo with AI)
1. **Plan → Produce → Validate → Register → Decide.**
2. For every task, prompt the AI as a **component** (Strategist, Data Engineer, Integrator).
3. Require outputs to conform to the **schemas** in `/schemas`.
4. Have the AI update: Deliverables, DAG changes, and Decision Log **in this file**.
5. Version every artifact (`vX.Y`) and keep checksums.

### Standard Component Prompt (copy-paste)
```
ROLE: You are the {component} for this project.
GOAL: Produce {artifact} at version {semver}.
INPUTS: This Control Doc (latest) + any attached files.
OUTPUT FORMAT: Exactly the {schema_name} schema if applicable. No commentary, no markdown.
TESTS: Include a minimal test plan and sample data.
REGISTRY: After output, update the Control Doc: artifact version, checksum (sha256), dependencies.
```
