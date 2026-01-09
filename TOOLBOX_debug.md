# Toolbox Protocol (MCP-Lite)

This document serves as the standard protocol for Agents working in this codebase.
**RULE:** When planning or executing refactors, ALWAYS consult this toolbox to ensure safety and preservation of legacy logic.

## 📦 Refactor Tools

*Location: `refactor_tools/`*

### 1. Golden Master (`GoldenMaster`)

**Purpose:** prevent regressions by recording behavior before changes and verifying after.
**When to use:** ALWAYS use this *before* touching complex, critical, or poorly understood functions.

**Usage:**

```python
from refactor_tools import GoldenMaster

# 1. SETUP (Pre-Refactor)
gm = GoldenMaster()
# Record outputs for various inputs
gm.record(
    func=target_function,
    inputs=[{"arg": "val1"}, {"arg": "val2"}],
    snapshot_name="target_func_v1"
)

# ... [Refactor Code] ...

# 2. VERIFY (Post-Refactor)
gm.verify(
    func=target_function,
    snapshot_name="target_func_v1"
)
```

### 2. Legacy Keeper (`LegacyKeeper`)

**Purpose:** Archive "Chesterton's Fences" - code that looks redundant but might have hidden purpose.
**When to use:** When deleting large chunks of code, or logic that seems "weird" but you aren't 100% sure is unused.

**Usage:**

```python
from refactor_tools import LegacyKeeper

keeper = LegacyKeeper()

# ARCHIVE CODE
keeper.archive_code(
    name="old_proxy_logic",
    code_content="... complex if/else block ...",
    reason="Replaced by new ProxyManager class. Kept for reference."
)

# LOG BEHAVIOR CHANGE
keeper.log_behavior(
    tag="REMOVED_DELAY",
    description="Removed 5s sleep. Verify if this causes rate limits."
)
```

### 3. Preservation Checklist (`PreservationChecklist`)

**Purpose:** Generate a checklist of behaviors that MUST be preserved during a task.
**When to use:** At the start of a `PLANNING` phase for significant refactors.

**Usage:**

```python
from refactor_tools import PreservationChecklist

checklist = PreservationChecklist()
checklist.add_item("Must handle empty JSON responses gracefully", critical=True)
checklist.add_item("Retries 3 times on 500 error", critical=True)
checklist.save_to_file("preservation_checklist.md")
```
