# 🛡️ Quality Assurance & Automated Auditing Protocol

## 🎯 Objective

To ensure **Smarketer Pro** meets the high standards of enterprise sales & marketing professionals by using autonomous agents to critique and verify the codebase.

## 🤖 The QA Bot (Static Analysis)

We use a specialized "UX Auditor" agent that reads the raw UI code and critiques it against a "Sales/Marketing Persona."

### How to Run

From the root directory:

```bash
python src/qa_bot.py --target all
```

### What it Does

1. **Scans** `src/ui/*.py` for Streamlit interface code.
2. **Simulates** a user persona (Sales Manager, Affiliate Marketer) reviewing the page.
3. **Identifies** missing buttons, dead ends, or lack of "Pro" features.
4. **Updates** `App_Punch_List.md` automatically with a new "🤖 AI Audit [Date]" section.

## 🧪 Dynamic Verification (Click-Testing)

*Currently in Beta.*
To verify that buttons actually work (click-testing), we use a headless browser session.

1. Ensure the app is running: `streamlit run src/app.py`
2. Run the clicker: `python tests/verify_clicks.py` (Requires Playwright)

## 📋 The Punch List Standard

The `App_Punch_List.md` is the single source of truth.

* **Human Entries**: Top of the list.
* **AI Entries**: Appended at the bottom with tags `[AI-Audit]`.
* **Resolution**: When fixing an item, change `[ ]` to `[x]` and move it to a "Completed" section (or delete it).

## 🚀 Definition of Done

A feature is "Done" when:

1. The QA Bot finds no critical "Missing Functionality" flags.
2. The `App_Punch_List.md` item is checked off.
3. The specific module (e.g., `crm_ui.py`) has been refactored using the Golden Master protocol.
