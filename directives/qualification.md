# Directive: Lead Qualification (The Gatekeeper)

**Goal**: Filter "Raw Candidates" down to "Qualified Leads" matching specific campaign criteria.
**Priority**: Accuracy. High Recall (don't miss good leads) is better than High Precision (rejecting bad ones) at this stage, but aim for both.

## Strategy

1. **Analyze Content**: Read the scraped text of the homepage.
2. **Check Criteria**: Compare strictly against the `User Provided Criteria`.
    - *Note*: The criteria changes per campaign. Do not assume "SaaS" or "Blue Collar".
3. **The "Instant NO" List** (Global Overrides):
    - Site is 404/Down.
    - Site is strictly a consumer blog / affiliate site (unless seeking influencers).
    - Site is a directory/aggregator (e.g. "Top 10 lists").

## Inputs

- `url`: The candidate URL.
- `content`: Scraped markdown of the page.
- `criteria`: The specific goals for this run (e.g. "Must be a dentist office with > 3 locations").

## Output

- `qualified`: Boolean.
- `reason`: Explanation of why it passed/failed.
- `score`: 0-100 relevance score.

## Execution Tool

- `orchestrator.py` (The LLM performs this reasoning directly).
