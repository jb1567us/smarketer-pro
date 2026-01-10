import json
import argparse
import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    import model_client
    from model_client import ModelClientError
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

SYSTEM_PROMPT = (
    "You are an AI project architect.\n"
    "Given a project idea, you must:\n"
    "- Create a list of roles.\n"
    "- For each role, include 3–7 high-value questions.\n"
    "- Include 3–10 global questions.\n"
    "Return ONLY valid JSON.\n"
)


def generate_team_and_questions(idea_text: str) -> dict:
    user_prompt = (
        "Project idea:\n"
        "----------------------\n"
        + idea_text
        + "\n----------------------\n\n"
        "Return JSON in this shape:\n\n"
        "{\n"
        '  \"project_title\": \"string\",\n'
        '  \"summary\": \"string\",\n'
        '  \"roles\": [\n'
        "    {\n"
        '      \"id\": \"snake_case\",\n'
        '      \"label\": \"string\",\n'
        '      \"purpose\": \"string\",\n'
        '      \"questions\": [\n'
        "        {\"id\": \"string\", \"text\": \"string\", \"priority\": 1}\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  \"global_questions\": [\n'
        "    {\"id\": \"string\", \"text\": \"string\", \"priority\": 1}\n"
        "  ]\n"
        "}\n"
    )
    content = model_client.generate_text(SYSTEM_PROMPT, user_prompt, task="planning").strip()
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json", "", 1).strip()
    return json.loads(content)


def build_answers_template(team_data: dict) -> dict:
    answers = {
        "project_title": team_data.get("project_title", ""),
        "summary": team_data.get("summary", ""),
        "answers": {},
        "global": [],
    }
    for role in team_data.get("roles", []):
        rid = role["id"]
        answers["answers"][rid] = {
            "role_label": role["label"],
            "purpose": role["purpose"],
            "questions": [],
        }
        for q in role.get("questions", []):
            answers["answers"][rid]["questions"].append(
                {
                    "question_id": q["id"],
                    "question_text": q["text"],
                    "priority": q.get("priority", 1),
                    "answer": "",
                }
            )
    for gq in team_data.get("global_questions", []):
        answers["global"].append(
            {
                "question_id": gq["id"],
                "question_text": gq["text"],
                "priority": gq.get("priority", 1),
                "answer": "",
            }
        )
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

    try:
        team_data = generate_team_and_questions(idea_text)
    except ModelClientError as e:
        raise SystemExit(f"Error generating team/questions: {e}")

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