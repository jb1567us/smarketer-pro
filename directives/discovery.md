# Directive: Lead Discovery (Broad Net Strategy)

**Goal**: Gather a large volume of potential leads ("Raw Candidates") from search engines.
**Priority**: Volume & Speed > Precision. (Precision happens in the Qualification phase).

## Strategy

1. **Search Broadly**: Use high-level keywords (e.g. "HVAC companies Dallas", not "Best commercial HVAC repair for fast food").
2. **Scrape Heavily**: Collect the top N results (e.g., 50-100) per query.
3. **Dumb Filter (Phase 1)**:
    - Exclude `gov`, `edu`, `org` (unless specified otherwise).
    - Exclude results from the global blocklist (e.g. `yelp.com`, `linkedin.com`, `yellowpages.com`).
    - Remove duplicates.
4. **Output**: A list of `Raw Candidate URLs` to be passed to the Qualification Agent.

## Inputs

- `keywords`: List of search terms.
- `niche`: Industry filter (optional).
- `limit`: Max results per keyword (Default: 50).

## Execution Tool

- `execution/search_targets.py`
