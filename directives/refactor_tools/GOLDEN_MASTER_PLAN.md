# Golden Master Grandmaster Plan

Establish a bulletproof safety net for the entire B2B Outreach Tool to enable fearless refactoring.

## Phase 1: Search & Harvester Coverage (COMPLETED)

- **Direct Scraper**: Snapshots of Google/DuckDuckGo SERP items.
- **Maps Parser**: Snapshots of List and Detail view extraction.

## Phase 2: Agent Lab Coverage (COMPLETED)

- **All Agents**: manager, researcher, influencer, copywriter.
- **Natural Language Mapping**: Captures `think_async` inputs to structured decisions.
- **Isolation**: Deep mocks for networking, DB, and harvester calls.

## Phase 3: Core & Social Infrastructure (COMPLETED)

- **Social Scraper**: Stats parsing and HTML metadata extraction.
- **Proxy Manager**: Configuration update logic.
- **Prompt Engine**: Template rendering consistency.
- **Workflow Engine**: DAG traversal and node execution flow.

## Implementation Details

### Directory Structure

```text
tests/golden_master/
├── snapshots/          # JSON Snapshots (Input + Expected Output + LLM History)
├── capture_agents.py   # Records Agent brains
├── capture_core.py     # Records PromptEngine & Workflow Engine
├── capture_social.py   # Records Social logic
├── runner.py           # Unified Grandmaster Runner
└── verify_*.py         # Individual component verifiers
```

### Usage Instructions

1. **Record**: `python tests/golden_master/capture_*.py`
2. **Verify**: `python tests/golden_master/runner.py`

### Safety Features

- **Deterministic**: LLM interactions are replayed from snapshots.
- **No Side Effects**: All database and network calls are mocked.
- **Windows Optimized**: UTF-8 hardened to support emojis in logs.

---
**Status: 100% Comprehensive Coverage Achieved.**
Ready for full-scale refactoring.
