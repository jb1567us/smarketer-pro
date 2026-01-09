# Refactor Tools

A safety net for aggressive refactoring. This package helps you implement the "Golden Master" technique and keep a history of "Chesterton's Fences" (legacy logic).

## Modules

### 1. Golden Master (`golden_master.py`)

Record the behavior of a function *before* you touch it. Verify it *after*.

```python
from refactor_tools import GoldenMaster

gm = GoldenMaster()

# 1. Record (do this BEFORE refactoring)
gm.record(
    func=my_complex_function,
    inputs=[{"arg1": 1}, {"arg1": 5}],
    snapshot_name="my_func_v1"
)

# 2. Verify (do this AFTER refactoring)
gm.verify(
    func=my_complex_function,
    snapshot_name="my_func_v1"
)
```

### 2. Legacy Keeper (`legacy_keeper.py`)

Don't just delete complex code. Archive it and log why.

```python
from refactor_tools import LegacyKeeper

keeper = LegacyKeeper()

# Archive a chunk of code you are removing
keeper.archive_code(
    name="proxy_rotation_logic",
    code_content="if status == 403: rotate_proxy() ...",
    reason="Replacing with smart-proxy-manager library"
)

# Just log a behavior change
keeper.log_behavior(
    tag="REMOVED_RETRY", 
    description="Removed the 3x retry on 404 errors because it was causing DDOS."
)
```

### 3. Preservation Checklist (`preservation.py`)

Generate a checklist of behaviors to preserve.

```python
from refactor_tools import PreservationChecklist

checklist = PreservationChecklist()
checklist.add_item("Must return None on empty string input", critical=True)
checklist.save_to_file("preservation_checklist.md")
```
