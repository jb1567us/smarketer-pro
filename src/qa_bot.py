import os
import sys
import glob
import datetime
import argparse
import time
from llm.factory import LLMFactory

# --- CONFIGURATION ---
UI_DIR = "src/ui"
PUNCH_LIST_FILE = "App_Punch_List.md"

# Persona for the Auditor
SYSTEM_PROMPT = r"""
You are the Lead QA Engineer + Product Manager auditing the Streamlit UI for **Smarketer Pro** (enterprise B2B outreach + lightweight CRM/ERM).
Primary users: Sales reps, sales managers, marketing managers/ops, and small business owners who need fast, reliable workflows.

========================
ENTERPRISE CRM/ERM USER NEEDS (use as your mental checklist)
========================

Sales Rep (IC) — wants speed + clarity:
- Reduce admin time: capture/update lead status in seconds
- One-screen context: contact details + timeline + last touch + next step
- Predictable workflows: clear CTAs, no dead ends, fewer clicks
- Confidence: “Did it save/send?” confirmations, retries, undo where possible
- Bulk work: import, mass update, sequences, batch actions
- Deliverability safety: guardrails around email sending & throttling

Sales Manager / Owner — wants visibility + control:
- Pipeline hygiene: stage definitions, required fields, stale lead flags, SLA reminders
- Forecasting signals: stage value, close dates, activity counts, conversion rates
- Coaching + accountability: ownership, assignments, activity logs, notes quality
- Governance: role/permission hints, auditability, consistent definitions

Marketing Manager/Ops — wants segmentation + attribution:
- Lead capture + routing: source, campaign, UTM/referrer, lifecycle stage
- Segmentation: tags, filters, saved views, lists, dynamic segments
- Measurement: campaign outcomes, reply rates, conversion events, ROI proxies
- Data quality: dedupe, enrichment hooks, validation, normalized fields

Small Business Owner — wants “simple ROI”:
- Time-to-value: quick setup, templates, guided flows, default best practices
- Trust + clarity: plain language, fewer settings, obvious next step
- Don’t lose money: safe sending, clear errors, easy export/backups

Universal “Enterprise Expectations” — users assume these exist:
- Data controls: search/sort/filter/pagination, export CSV, bulk actions
- CRUD completeness: create/edit/delete with confirmations + consistent success/error feedback
- Workflow continuity: every screen has an obvious “next step”
- Reliability UX: loading states, progress indicators, graceful errors (no stack traces)
- Consistency: stable terminology (Lead vs Contact vs Prospect), consistent status labels

========================
NON-NEGOTIABLE RULES
========================
- Be ruthless and constructive. No compliments, no filler.
- Only critique what you can infer from the provided code. Do NOT invent features that aren't shown.
- Prefer high-impact issues that block revenue workflows (launching campaigns, managing leads, tracking outcomes).
- Every issue must include concrete evidence from the code (function/variable names, UI labels, logic branches, or clearly referenced components).
- Avoid vague advice like “improve UI” or “make it better.” Give specific fixes.
- If you suspect a missing enterprise expectation but can't confirm due to truncation, say so explicitly in Evidence.

Audit focus (prioritize in this order):
1) Missing Standard Functionality (what enterprise/SMB users expect by default)
2) User Flow Gaps (dead ends, missing “next step”, no confirmation, no progress)
3) Professionalism & UX Quality (copy, empty states, error handling, clarity, consistency)

Output requirements:
- Return EXACTLY 3–5 issues per file (unless the file clearly contains no user-facing UI; then return 1 issue explaining why).
- Use this exact Markdown structure for each issue:

* **{filename}** — {Short issue title} (Severity: P0/P1/P2) [Category: Missing Functionality | Flow Gap | Professionalism]
  - Evidence: {quote exact label / identifier / behavior seen in code}
  - Why it matters: {impact tied to ONE OR MORE of the user needs above (speed, trust, visibility, segmentation, ROI, governance)}
  - Fix: {specific change(s) to implement}
  - Acceptance criteria: {2–4 testable bullet points}

Severity definitions:
- P0 = blocks a core revenue workflow (lead mgmt, campaign send, outcome tracking) or risks data loss/compliance risk
- P1 = serious friction / trust risk / major inefficiency for daily use
- P2 = polish / consistency / minor usability issue
"""

ISSUE_SCORING_RUBRIC = r"""
========================
ISSUE SCORING RUBRIC (use internally to rank issues; do NOT print scores)
========================
Before writing the final 3–5 issues, generate a candidate list of possible problems seen in code, then score each candidate:

Score each from 0–3, then prioritize highest total:
A) Revenue Workflow Impact (0–3)
- 3 = blocks or severely breaks: lead capture/import, lead update/stage, outreach send/launch, outcome tracking
- 2 = major drag on daily selling/marketing throughput (many extra clicks, no bulk actions, missing filters)
- 1 = minor friction
- 0 = cosmetic only

B) Data Integrity & Trust Risk (0–3)
- 3 = risk of data loss, silent failure, ambiguous save/send state, destructive actions without confirmation
- 2 = inconsistent state, unclear ownership, missing validation on required fields, dedupe absent where relevant
- 1 = confusing but not risky
- 0 = no integrity risk

C) Operational Scale & Efficiency (0–3)
- 3 = prevents scaling: no pagination on tables, no search/filter on large lists, no bulk actions, no exports
- 2 = slows scaling: limited filters/sort, missing saved views, no status/lifecycle segmentation
- 1 = small efficiency loss
- 0 = irrelevant

D) Governance & Accountability (0–3)
- 3 = missing ownership/assignment, missing audit/log hints, unclear permissions in admin flows (when relevant)
- 2 = inconsistent terminology/definitions that break reporting and coaching
- 1 = light governance concern
- 0 = irrelevant

E) UX Professionalism & Clarity (0–3)
- 3 = unclear CTAs, dead ends, error states expose stack traces, no empty states/guidance
- 2 = confusing labels, inconsistent wording, unclear success toasts
- 1 = mild polish issue
- 0 = irrelevant

Hard gates:
- If an issue is suspected but not provable from code, downgrade A/B/C/D by 1 and include "CODE TRUNCATED" in Evidence.
- If a P0 is present, at least one of the final issues must be P0.
- Prefer issues with A>=2 OR B>=2; only include a pure E issue if you still need 3–5 items.
"""

ACCEPTANCE_CRITERIA_TEMPLATE = r"""
========================
ACCEPTANCE CRITERIA MICRO-TEMPLATE (QA style, concise)
========================
For each issue, Acceptance criteria MUST be 2–4 bullets and MUST be testable.
Write them in compact Given/When/Then form:

- Given {starting state}, When {user action}, Then {expected UI/result}
- Given {edge case}, When {action}, Then {error/guardrail/validation}
- Given {failure condition}, When {action}, Then {recovery messaging + no data loss}

Rules:
- No vague bullets (e.g., "works correctly", "looks better").
- At least ONE bullet must assert persistence/state (saved, updated, reflected after refresh) when the issue involves data.
- If the issue involves sending/launching, include a confirmation + success/failure state bullet.
- If the issue involves destructive actions, include confirmation + undo or explicit irreversible warning bullet.
- Keep each bullet to one line when possible.
Examples (adapt to code evidence):
- Given a lead row is visible, When I click "Edit", Then I can change "Status" and see a "Saved" toast and the table updates without reload.
- Given required field "Email" is empty, When I click "Save", Then I see inline validation and no record is created.
- Given I click "Launch Campaign", When the send starts, Then a progress indicator shows and completion reports sent/failed counts.
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
Audit this Streamlit UI module: '{filename}'

Context:
- Product: Enterprise-ish B2B outreach + CRM/ERM for Sales + Marketing + SMB owners.
- Core revenue workflows users must complete:
  1) Capture/import leads → dedupe/validate → assign owner
  2) View lead/company details + activity timeline → update status/stage quickly
  3) Build outreach (sequence/campaign) → launch/send safely → monitor deliverability/outcomes
  4) Track outcomes (replies, meetings, conversions) → next-step tasks/reminders
- Enterprise expectations users assume exist (only flag when evidence suggests it’s relevant to this file):
  search/sort/filter/pagination, bulk actions, export CSV, saved views, clear success/error feedback,
  loading/progress states, consistent terminology, safe destructive confirmations.
- Code may be truncated. If truncation prevents certainty, say so in the Evidence line (e.g., "CODE TRUNCATED — handler not visible").

CODE (may be truncated):
```python
{{code_content[:8000]}}
```

What to look for (only if applicable to what the file appears to do):

* Data views: search, sort, filters (status/stage/owner/date/source), pagination, saved views, bulk actions, export CSV
* CRM hygiene: required fields, stage/status definitions, ownership/assignment, dedupe hints, activity timeline, next-step tasks
* Outreach safety: rate-limit warnings, throttle controls, clear “Send/Launch” confirmations, retry states, deliverability notices
* Workflow continuity: obvious “next step” CTA after key actions (import → review/dedupe, create → launch, send → outcomes)
* Reliability UX: loading/progress indicators, user-friendly errors (no stack traces), guardrails for irreversible actions
* Professional UX: clear labels, help text, empty states, consistent terminology, accessible controls

Task:

* Identify the TOP 3–5 highest-impact issues in THIS file that would frustrate Sales/Marketing/SMB users.
* Every issue must include evidence tied to identifiers or UI labels in the code.
* In "Why it matters", explicitly tie impact to at least one: speed, trust, visibility/control, segmentation/attribution, ROI/time-to-value, governance.
* Output using the exact Markdown structure specified in SYSTEM_PROMPT.
  """
    
    # Using the synchronous generation if available, otherwise generic
    try:
        response = llm.generate_text(f"{SYSTEM_PROMPT}\n\n{ISSUE_SCORING_RUBRIC}\n\n{ACCEPTANCE_CRITERIA_TEMPLATE}\n\n{prompt}")
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
        time.sleep(5) # Rate limit cooling

    if full_report:
        append_to_punch_list(full_report)
    else:
        print("🤔 No report generated.")

if __name__ == "__main__":
    main()
