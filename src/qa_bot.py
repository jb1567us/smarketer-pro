import os
import sys
import glob
import datetime
import argparse
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
    parser = argparse.ArgumentParser(description="Smarketer Pro QA Bot")
    parser.add_argument("--target", type=str, default=["all"], nargs='+', help="UI files to analyze (default: all)")
    args = parser.parse_args()

    print("🤖 Smarketer Pro QA Bot Initializing...")
    
    # Initialize your existing LLM infrastructure
    try:
        llm = LLMFactory.get_provider()
    except Exception as e:
        print(f"❌ LLM Setup Failed: {e}")
        return

    # Find UI files
    if "all" in args.target:
        ui_files = glob.glob(os.path.join(UI_DIR, "*_ui.py"))
    else:
        ui_files = []
        for t in args.target:
            target_path = os.path.join(UI_DIR, t if t.endswith(".py") else f"{t}.py")
            if os.path.exists(target_path):
                ui_files.append(target_path)
            else:
                print(f"❌ Target file not found: {target_path}")
    
    if not ui_files:
        print(f"❌ No UI files found in {UI_DIR}")
        return

    full_report = ""
    for ui_file in ui_files:
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
