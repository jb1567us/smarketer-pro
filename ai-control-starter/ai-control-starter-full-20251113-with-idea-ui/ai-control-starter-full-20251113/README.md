# AI Control Starter – Full Version

This repo is a **file-first control system** for using AI to build complex projects
(marketing campaigns, full software products, etc.) in a structured, semi- or fully-automated way.

It adds two layers on top of the basic starter:

1. **Idea → Virtual Team & Questions (bootstrap)**
2. **Answers → Project Control Doc (`control.md`)**
3. **Control Doc → Concrete Artifacts (code, JSON, plans) via AI-driven scripts**

## High-Level Flow

1. **Describe your idea** in `idea.txt` (root or `artifacts/`).
2. Run **bootstrap script** to generate a *virtual team* and *questions*:
   ```bash
   python scripts/bootstrap_team_and_questions.py --idea idea.txt
   ```
   This writes:
   - `artifacts/team_and_questions_v0.1.json`
   - `artifacts/intake_answers_template_v0.1.json`

3. **Answer the questions** by editing the template and saving it as:
   ```text
   artifacts/intake_answers_v0.1.json
   ```

4. Generate a tailored **Control Doc** for this project:
   ```bash
   python scripts/generate_control_doc.py --idea idea.txt
   ```
   This writes (or overwrites) the root `control.md`.

5. Use **artifact scripts** (you can add more) to generate concrete outputs
   based on `control.md` and the schemas in `/schemas`.

6. Validate JSON/JSONL artifacts:
   ```bash
   python scripts/validate_json.py --schema creativespec --in artifacts/D4_creatives_v0.1.jsonl
   ```

## Requirements

- Python 3.10+
- `pip install openai jsonschema`

You must set your OpenAI API key in the environment before running the AI scripts, e.g.:

```bash
export OPENAI_API_KEY="sk-..."
# or on Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
```

## Key Files & Folders

```
ai-control-starter-full-20251113/
  control.md                 # Generated project Control Doc (source of truth)
  idea.txt                   # (You create) your raw project idea
  /artifacts/
    team_and_questions_v0.1.json
    intake_answers_template_v0.1.json
    intake_answers_v0.1.json
    ... (generated artifacts: JSONL, .py, .md, etc.)
  /schemas/
    leadrecord.schema.json
    creativespec.schema.json
    trackingevent.schema.json
  /scripts/
    bootstrap_team_and_questions.py   # Idea → virtual team + questions
    generate_control_doc.py           # Idea + answers → control.md
    validate_json.py                  # Schema validation for artifacts
    ... (you can add generate_*.py scripts here)
  /tests/
    TESTPLAN.md
  /docs/
    ... (any supplementary documentation)
```

## Next Steps

- Start with a simple project idea (e.g., "customer discovery SaaS for local restaurants").
- Run the bootstrap → answer questions → generate Control Doc pipeline.
- Then add role-specific generator scripts such as:
  - `generate_backend_api.py`
  - `generate_frontend_ui.py`
  - `generate_marketing_creatives.py`

Each of those should:
- Read `control.md` (and any relevant schemas),
- Call the OpenAI API with a strong, role-specific prompt,
- Save outputs to `/artifacts`,
- Optionally run `validate_json.py` or other tests,
- And prompt you to update `control.md` (version, checksum, decisions).
