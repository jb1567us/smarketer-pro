# AI Control Starter – UI + Ollama

This repo is a **file-first control system** for using AI to build complex projects
(marketing campaigns, full software products, etc.) with a **browser UI** and a
**local Ollama model** (no paid OpenAI API required).

It supports:

1. **Idea → Virtual Team & Questions (via Flask UI + Ollama)**
2. **Answers → Project Control Doc (`control.md`)**
3. **Control Doc → Role-specific artifacts (auto-generated scripts per role)**

---

## Quick Setup

### 1. Install dependencies

Make sure Python 3.10+ is installed and on your PATH, then run:

```bat
install.bat
```

This installs packages from `requirements.txt`:

- `flask`
- `jsonschema`
- `requests`
- `psutil`

### 2. Ensure Ollama is running

Install and run [Ollama](https://ollama.com/) and pull a model, for example:

```bat
ollama pull llama3
```

You can configure which model to use automatically via the model auto-config step
(see below), or manually by editing `model_config.json`.

---

## Main Flow (UI-first, with Ollama)

### Step 0 – Auto-configure models (recommended once)

Run:

```bat
run.bat
```

Choose:

```text
5. Auto-configure models with Ollama
```

This script:

- Detects your RAM size
- Chooses a profile (tiny, small, medium, large)
- Chooses appropriate models for:
  - `planning`
  - `coding`
  - `utility`
- Calls `ollama list` to see installed models
- Runs `ollama pull <model>` for any missing recommended model
- Writes `model_config.json` with the chosen models

All other scripts then use these settings.

### Step 1 – Start the web UI

Run:

```bat
run.bat
```

Choose:

```text
2. Open web UI (enter idea + fill answers in browser)  [RECOMMENDED]
```

This starts a Flask app on `http://127.0.0.1:5000/`.

#### 1A. Enter your idea

At `/` (home):

- Type your idea into the textarea.
- Click **“Generate Team & Questions”**.

The system uses the `planning` model (via `model_client.py`) to:

- Save your idea to `idea.txt`
- Create `artifacts/team_and_questions_v0.1.json` (virtual team + questions)
- Initialize `artifacts/intake_answers_v0.1.json` (empty answers template)

#### 1B. Answer the questions

You’re redirected to `/questions`, where you:

- See each role’s questions as a form
- See global questions
- Fill in your answers
- Click **“Save Answers”**

This writes:

- `artifacts/intake_answers_v0.1.json` (with your answers)

You never edit JSON directly.

---

### Step 2 – Generate `control.md`

Back in the terminal, run:

```bat
run.bat
```

Choose:

```text
3. Generate control.md from your answers
```

This calls `scripts/generate_control_doc.py`, which uses the `planning` model
to create a full Markdown control doc at `control.md` based on:

- `idea.txt`
- `artifacts/team_and_questions_v0.1.json`
- `artifacts/intake_answers_v0.1.json`

`control.md` becomes the **source of truth** for all further AI work.

---

### Step 3 – Auto-create generator scripts for each role

Then run:

```bat
run.bat
```

Choose:

```text
4. Auto-create role-specific generator scripts
```

This creates one script per role:

- `scripts/gen_<role_id>.py` (e.g. `gen_product_manager.py`, `gen_backend_engineer.py`)

Each generated script:

- Reads `control.md`
- Uses `model_client.generate_text(..., task="coding")` (coding model)
- Writes a Markdown artifact to `artifacts/<role_id}_artifact_v0.1.md`

You can run any of them directly, for example:

```bat
python scripts\gen_backend_engineer.py
```

---

## Model Backend Overview

All model calls go through `model_client.py`:

- Default backend: **Ollama**
- Config via `model_config.json`:
  - `backend` (currently `"ollama"`)
  - `default_model`
  - `tasks` mapping, e.g.:
    - `"planning"`: `"llama3"`
    - `"coding"`: `"codellama"`
    - `"utility"`: `"phi3"`

You can regenerate `model_config.json` by running:

```bat
run.bat
```

option 5 again, or edit it by hand.

---

## Validation & Schemas

The `/schemas` folder includes sample JSON Schema files for marketing-style
artifacts:

- `leadrecord.schema.json`
- `creativespec.schema.json`
- `trackingevent.schema.json`

Use `scripts/validate_json.py` to validate artifacts:

```bat
python scripts\validate_json.py --schema creativespec --in artifacts\my_creatives.jsonl
```

---

## Tests

Use `/tests/TESTPLAN.md` for a lightweight manual or automated testing plan
for your project. You can also add automated tests later.
