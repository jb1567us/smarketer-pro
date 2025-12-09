# AI Control Starter

A minimal, file-first system for managing complex, multi-part AI work via a single **Control Doc**, strict **schemas**, and a simple **governance loop**.

## Structure
```
ai-control-starter-20251113/
  control.md
  /artifacts/           # versioned outputs (D1_..., D2_...)
  /schemas/             # JSON Schemas for I/O
  /scripts/             # validator and helpers
  /tests/               # put minimal test plans here
  /docs/                # any supplementary docs
```

## Quick Start
1. Edit `control.md` → fill **Objective**, **Constraints**, and **Open Questions**.
2. Use the **Standard Component Prompt** in `control.md` for each sub-task.
3. Validate outputs with:
   ```bash
   pip install jsonschema
   python scripts/validate_json.py --schema creativespec --in artifacts/creatives.jsonl
   ```
4. After each output, update **Deliverables**, **DAG**, and **Decision Log** in `control.md`.

## Notes
- Keep artifacts as plain files (JSONL/MD/YAML/PY) to maintain tool-agnostic portability.
- Use semantic versions (`vX.Y`) and checksums to track integrity.
