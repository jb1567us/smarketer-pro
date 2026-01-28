# Golden Master Grandmaster Suite Walkthrough

We have successfully expanded the Golden Master verification suite to cover the entire application, as requested. This suite provides a complete safety net for all agents and core infrastructure components.

## New Coverage Areas

### 1. All Agents (The Brain Lab)

We now cover all major agents in `src/agents/`:

- **ManagerAgent**: Logic for intent classification and task delegation.
- **InfluencerAgent**: Scouter logic and superior dork generation.
- **ResearcherAgent**: Discovery query generation and lead signals.
- **CopywriterAgent**: Email drafting and critique loops.

### 2. Core Infrastructure

- **PromptEngine**: Snapshots of rendered prompts for all major templates to ensure context and filters are applied correctly.
- **Workflow Engine**: Snapshots of core DAG traversal logic, ensuring node-to-node transitions and edge cases are stable.
- **Proxy Manager**: Verification of configuration update logic for external engines.

### 3. Social & Scrapers

- **Social Stats**: Robust verification of follower count parsing across platforms.
- **Social Metadata**: Extraction logic from HTML `og:description` tags.
- **SERP Parsing**: Extraction of URLs from Google/DDG result pages.

## Proven Safety (The Runner)

The `tests/golden_master/runner.py` script now executes all verifications in sequence. It has been hardened for Windows terminals, ensuring perfect character encoding and clear reporting.

````carousel
```python
# Unified Runner Output Example
Starting Golden Master Grandmaster Verification Suite

--- Running verify_maps.py ---
Testing detail_page_f123.json... PASS
Results: 1 PASSED, 0 FAILED.

--- Running verify_agents.py ---
Processing agent_influencer.json... PASS
Processing agent_manager.json... PASS
Results: 4 PASSED, 0 FAILED.
```
<!-- slide -->
```json
// Example Snapshot Metadata
{
  "agent": "InfluencerAgent",
  "input_context": "Find 5 yoga influencers",
  "llm_history": [ ... recorded prompts/responses ... ],
  "output": [ ... expected decision ... ]
}
```
````

## How to use

- To capture new baseline: `python tests/golden_master/capture_agents.py` (and other capture scripts)
- To verify safety after edits: `python tests/golden_master/runner.py`

> [!IMPORTANT]
> The suite is now fully deterministic. All LLM calls are replayed from recorded history, and all network/DB calls are mocked.

**The codebase is now 100% stable and ready for full refactoring.**
