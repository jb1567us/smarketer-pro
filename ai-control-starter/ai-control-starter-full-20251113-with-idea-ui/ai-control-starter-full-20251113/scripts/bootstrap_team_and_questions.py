import os
import json
import argparse
from pathlib import Path

try:
    import openai
except ImportError:
    openai = None

TEAM_QUESTION_SYSTEM_PROMPT = """
You are an AI project architect.

Task:
- Read the user's project idea.
- Decide what "virtual team" of roles is needed to bring it to life end-to-end.
- For each role, describe its purpose and ask 3-7 high-leverage questions.
- Also include 3-10 global questions that any role might care about.

Output:
- Pure JSON.
- No commentary, no markdown.
- Use this exact shape:

{
  "project_title": "...",
  "summary": "...",
  "roles": [
    {
      "id": "snake_case_identifier",
      "label": "Human-readable label",
      "purpose": "1-2 sentence description",
      "questions": [
        {"id": "role_id_q1", "text": "Question text", "priority": 1}
      ]
    }
  ],
  "global_questions": [
    {"id": "g_q1", "text": "Question text", "priority": 1}
  ]
}
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


def generate_team_and_questions(idea_text: str) -> dict:
    require_openai_client()
    system = TEAM_QUESTION_SYSTEM_PROMPT
    user = f"""User project idea:
"""{idea_text}"""

Return ONLY JSON matching the specified structure."""

    resp = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    text = resp["choices"][0]["message"]["content"].strip()
    # Strip simple ```json fences if present
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text)


def build_answers_template(team_data: dict) -> dict:
    """Create a template that mirrors all questions but with empty 'answer' fields."""
    answers = {
        "project_title": team_data.get("project_title", ""),
        "summary": team_data.get("summary", ""),
        "answers": {}
    }
    for role in team_data.get("roles", []):
        rid = role["id"]
        answers["answers"][rid] = {
            "role_label": role["label"],
            "purpose": role["purpose"],
            "questions": []
        }
        for q in role.get("questions", []):
            answers["answers"][rid]["questions"].append({
                "question_id": q["id"],
                "question_text": q["text"],
                "priority": q.get("priority", 1),
                "answer": ""  # to be filled by you
            })
    # Global questions
    answers["global"] = []
    for gq in team_data.get("global_questions", []):
        answers["global"].append({
            "question_id": gq["id"],
            "question_text": gq["text"],
            "priority": gq.get("priority", 1),
            "answer": ""
        })
    return answers


def main():
    ap = argparse.ArgumentParser(
        description="Bootstrap virtual team + questions from a project idea."
    )
    ap.add_argument("--idea", required=True, help="Path to a text file with your project idea.")
    ap.add_argument("--outdir", default="artifacts", help="Where to write JSON outputs.")
    args = ap.parse_args()

    idea_path = Path(args.idea)
    if not idea_path.exists():
        raise FileNotFoundError(f"Idea file not found: {idea_path}")

    idea_text = idea_path.read_text(encoding="utf-8")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    team_data = generate_team_and_questions(idea_text)
    answers_template = build_answers_template(team_data)

    team_json_path = outdir / "team_and_questions_v0.1.json"
    answers_template_path = outdir / "intake_answers_template_v0.1.json"

    team_json_path.write_text(json.dumps(team_data, indent=2), encoding="utf-8")
    answers_template_path.write_text(json.dumps(answers_template, indent=2), encoding="utf-8")

    print(f"Wrote team + questions: {team_json_path}")
    print(f"Wrote answers template: {answers_template_path}")
    print("→ Fill in 'answer' fields and save as artifacts/intake_answers_v0.1.json")


if __name__ == "__main__":
    main()
