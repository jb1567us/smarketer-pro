Based on your "Agentic" architecture and the request for a tool that proactively analyzes your app, I have created two things for you:

1. **The Directive (`directives/QA_PROTOCOL.md`)**: A standard operating procedure for maintaining quality.
2. **The QA Bot (`src/qa_bot.py`)**: A script that uses your *existing* LLM infrastructure to read your UI code (`src/ui/*.py`), critique it from the perspective of a Sales/Marketing pro, and automatically append items to your `App_Punch_List.md`.

You can create these files in your IDE.

### 1. The Directive

Create a new file at `directives/QA_PROTOCOL.md`. This formally defines how your "Anti-Gravity" development process works.

```markdown
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

```

---

### 2. The QA Bot Script

Create this file at `src/qa_bot.py`. This script connects to your existing `LLMFactory` so it "thinks" using the same brain as your other agents.

```python
import os
import sys
import glob
import datetime
from llm.factory import LLMFactory

# --- CONFIGURATION ---
UI_DIR = "src/ui"
PUNCH_LIST_FILE = "App_Punch_List.md"

# Persona for the Auditor
SYSTEM_PROMPT = """
You are the Lead QA Engineer and Product Manager for 'Smarketer Pro', an enterprise B2B outreach and CRM platform. 
Your users are busy Salespeople, Marketing Managers, and Small Business Owners.

Your Goal: Analyze the provided Python/Streamlit UI code. 
Critique it strictly on:
1. **Missing Standard Functionality**: (e.g., A CRM table with no 'Edit' button? A dashboard with no date filter?)
2. **User Flow Gaps**: (e.g., "After creating a campaign, there is no button to launch it.")
3. **Professionalism**: (e.g., "Error messages look too technical.")

Format your response as a list of actionable bullet points. Do not compliment the code. Be ruthless but constructive.
"""

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def append_to_punch_list(report):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"\n\n## 🤖 AI Audit Report ({timestamp})\n"
    
    with open(PUNCH_LIST_FILE, "a", encoding="utf-8") as f:
        f.write(header)
        f.write(report)
        f.write("\n\n---\n")
    print(f"✅ Updated {PUNCH_LIST_FILE}")

def analyze_ui_file(llm, filepath):
    filename = os.path.basename(filepath)
    print(f"🔍 Analyzing {filename}...")
    
    code_content = read_file(filepath)
    
    prompt = f"""
    Analyze this UI file: '{filename}'
    
    CODE:
    ```python
    {code_content[:8000]} # Truncated if too long
    ```
    
    Identify 3-5 critical missing features or UX flaws for a Sales/Marketing user.
    Output format:
    * **{filename}**: [Issue] - [Why it matters]
    """
    
    # Using the synchronous generation if available, otherwise generic
    try:
        response = llm.generate_text(f"{SYSTEM_PROMPT}\n\n{prompt}")
        return response
    except Exception as e:
        return f"* **{filename}**: ⚠️ Could not analyze due to error: {str(e)}"

def main():
    print("🤖 Smarketer Pro QA Bot Initializing...")
    
    # Initialize your existing LLM infrastructure
    # Assuming config.yaml is set up correctly
    try:
        llm = LLMFactory.create_provider("openai") # Or 'gemini', 'groq' based on your config
    except Exception as e:
        print(f"❌ LLM Setup Failed: {e}")
        print("Tip: Check your config.yaml and environment variables.")
        return

    # Find all UI files
    ui_files = glob.glob(os.path.join(UI_DIR, "*_ui.py"))
    
    if not ui_files:
        print(f"❌ No UI files found in {UI_DIR}")
        return

    full_report = ""
    
    for ui_file in ui_files:
        # Skip internal utility files if necessary
        if "styles.py" in ui_file or "components.py" in ui_file:
            continue
            
        report_segment = analyze_ui_file(llm, ui_file)
        full_report += report_segment + "\n"
        print(f"   > Done with {os.path.basename(ui_file)}")

    if full_report:
        append_to_punch_list(full_report)
    else:
        print("🤔 No report generated.")

if __name__ == "__main__":
    main()

```

### How to use this now:

1. **Configure**: Ensure your `config.yaml` has a valid LLM provider set up (based on your uploaded `config.yaml`, it looks like you support Gemini/OpenAI/Groq).
2. **Run**: In your terminal, run `python src/qa_bot.py`.
3. **Review**: Open `App_Punch_List.md`. You will see a new section at the bottom where the bot has identified specific gaps (e.g., "crm_ui.py: Missing 'Export to CSV' button for leads").