import os
import json
import argparse
from pathlib import Path

try:
    import openai
except ImportError:
    openai = None

CONTROL_DOC_PROMPT = """
You are an expert project architect and technical lead.

You will receive:
- The raw project idea.
- A JSON description of the virtual team and their questions.
- A JSON file with the user's answers to all questions.

Goal:
- Generate a complete `control.md` for this project, suitable to live at the repo root.
- This Control Doc will be used by multiple AI "roles" to build a full product.

Structure of control.md:
1. # Project Control Doc
2. ## Objective
   - 1–3 bullet points, measurable.
3. ## Scope & Non-Goals
4. ## Roles & Responsibilities
   - Bullet list mapping role ids → responsibilities.
5. ## Deliverables (artifact registry)
   - D1, D2, ... with clear names, owners (roles), and brief descriptions.
6. ## Task Graph (DAG)
   - List tasks T1, T2, ... and their dependencies.
7. ## Interface Contracts (I/O Schemas)
   - Assume schemas live in /schemas; describe what each covers even if not yet created.
8. ## Constraints
   - Budget, timelines, tech stack, risk constraints inferred from answers.
9. ## Decision Log
   - Seed with 2–5 initial decisions derived from user's answers.
10. ## Open Questions
   - Anything still unclear that should be resolved before heavy implementation.

Rules:
- Output VALID Markdown only.
- No extra commentary outside the doc.
- Make it specific and pragmatic, not vague.
"""


def require_openai_client():
    if openai is None:
        raise RuntimeError(
            "The 'openai' package is not installed. Install it with:\n"
            "  pip install openai"
        )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Set it before running this script."
        )
    openai.api_key = api_key


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser(
        description="Generate a project-specific control.md from idea + Q&A JSON."
    )
    ap.add_argument("--idea", required=True, help="Path to idea.txt")
    ap.add_argument("--team", default="artifacts/team_and_questions_v0.1.json",
                    help="Path to team_and_questions JSON")
    ap.add_argument("--answers", default="artifacts/intake_answers_v0.1.json",
                    help="Path to filled intake answers JSON")
    ap.add_argument("--out", default="control.md", help="Where to write the Control Doc")
    args = ap.parse_args()

    idea_path = Path(args.idea)
    if not idea_path.exists():
        raise FileNotFoundError(f"Idea file not found: {idea_path}")
    team_path = Path(args.team)
    answers_path = Path(args.answers)
    if not team_path.exists():
        raise FileNotFoundError(f"Team JSON not found: {team_path}")
    if not answers_path.exists():
        raise FileNotFoundError(f"Answers JSON not found: {answers_path}")

    idea_text = idea_path.read_text(encoding="utf-8")
    team_data = load_json(team_path)
    answers_data = load_json(answers_path)

    combined_context = {
        "idea": idea_text,
        "team": team_data,
        "answers": answers_data,
    }

    require_openai_client()

    prompt = (
        CONTROL_DOC_PROMPT
        + "\n\nHere is the combined JSON context:\n\n"
        + json.dumps(combined_context, indent=2)
        + "\n\nNow output the complete control.md."
    )

    resp = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You generate precise Markdown documents."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    control_md = resp["choices"][0]["message"]["content"]
    out_path = Path(args.out)
    out_path.write_text(control_md, encoding="utf-8")

    print(f"Wrote Control Doc to: {out_path}")


if __name__ == "__main__":
    main()
