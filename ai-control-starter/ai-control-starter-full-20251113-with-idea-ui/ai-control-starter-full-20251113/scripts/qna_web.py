import os
import json
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash

# Optional OpenAI import (required for idea -> team bootstrap)
try:
    import openai
except ImportError:
    openai = None

BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BASE_DIR / "artifacts"

TEAM_FILE = ARTIFACTS_DIR / "team_and_questions_v0.1.json"
ANSWERS_FILE = ARTIFACTS_DIR / "intake_answers_v0.1.json"
IDEA_FILE = BASE_DIR / "idea.txt"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = "change-me-if-you-want"  # used for flash messages


TEAM_QUESTION_SYSTEM_PROMPT = """You are an AI project architect.

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
    """Call OpenAI to generate team + questions JSON from idea text."""
    require_openai_client()
    system = TEAM_QUESTION_SYSTEM_PROMPT
    user = f"""User project idea:
"""{idea_text}"""


Return ONLY JSON matching the specified structure."""  # noqa: E501

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


def load_team():
    if not TEAM_FILE.exists():
        raise FileNotFoundError(
            f"{TEAM_FILE} not found. Start at the idea step to generate it."
        )
    return json.loads(TEAM_FILE.read_text(encoding="utf-8"))


def load_existing_answers(team_data):
    """If an answers file exists, load it and prefill; otherwise build an empty structure."""
    if ANSWERS_FILE.exists():
        answers_data = json.loads(ANSWERS_FILE.read_text(encoding="utf-8"))
    else:
        answers_data = {
            "project_title": team_data.get("project_title", ""),
            "summary": team_data.get("summary", ""),
            "answers": {},
            "global": [],
        }

    answers_data.setdefault("answers", {})

    # Role-specific questions
    for role in team_data.get("roles", []):
        rid = role["id"]
        if rid not in answers_data["answers"]:
            answers_data["answers"][rid] = {
                "role_label": role["label"],
                "purpose": role["purpose"],
                "questions": [],
            }

        existing_by_id = {
            q["question_id"]: q
            for q in answers_data["answers"][rid].get("questions", [])
        }

        merged_questions = []
        for q in role.get("questions", []):
            qid = q["id"]
            existing = existing_by_id.get(qid, {})
            merged_questions.append(
                {
                    "question_id": qid,
                    "question_text": q["text"],
                    "priority": q.get("priority", 1),
                    "answer": existing.get("answer", ""),
                }
            )
        answers_data["answers"][rid]["questions"] = merged_questions

    # Global questions
    existing_global = {q["question_id"]: q for q in answers_data.get("global", [])}
    merged_global = []
    for gq in team_data.get("global_questions", []):
        qid = gq["id"]
        existing = existing_global.get(qid, {})
        merged_global.append(
            {
                "question_id": qid,
                "question_text": gq["text"],
                "priority": gq.get("priority", 1),
                "answer": existing.get("answer", ""),
            }
        )
    answers_data["global"] = merged_global

    return answers_data


@app.route("/", methods=["GET", "POST"])
def idea_form():
    """First step: capture the raw project idea and generate team + questions."""
    existing_idea = ""
    if IDEA_FILE.exists():
        existing_idea = IDEA_FILE.read_text(encoding="utf-8")

    if request.method == "POST":
        idea_text = request.form.get("idea_text", "").strip()
        if not idea_text:
            flash("Please enter your idea before continuing.", "error")
            return render_template("idea_form.html", idea_text=existing_idea)

        # Save idea.txt
        IDEA_FILE.write_text(idea_text, encoding="utf-8")

        try:
            team_data = generate_team_and_questions(idea_text)
        except Exception as e:
            flash(f"Error generating team/questions: {e}", "error")
            return render_template("idea_form.html", idea_text=idea_text)

        # Save team_and_questions JSON
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        TEAM_FILE.write_text(json.dumps(team_data, indent=2), encoding="utf-8")

        # Initialize answers template
        answers_template = build_answers_template(team_data)
        ANSWERS_FILE.write_text(json.dumps(answers_template, indent=2), encoding="utf-8")

        flash("Generated team and questions from your idea. Now answer them.", "success")
        return redirect(url_for("qna_form"))

    # GET
    return render_template("idea_form.html", idea_text=existing_idea)


@app.route("/questions", methods=["GET", "POST"])
def qna_form():
    """Second step: show Q&A form based on generated team/questions."""
    try:
        team_data = load_team()
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for("idea_form"))

    if request.method == "POST":
        project_title = request.form.get("project_title", "").strip()
        summary = request.form.get("summary", "").strip()

        answers_data = {
            "project_title": project_title or team_data.get("project_title", ""),
            "summary": summary or team_data.get("summary", ""),
            "answers": {},
            "global": [],
        }

        # Role-specific answers
        for role in team_data.get("roles", []):
            rid = role["id"]
            role_label = role["label"]
            purpose = role["purpose"]
            role_questions = []
            for q in role.get("questions", []):
                qid = q["id"]
                field_name = f"{rid}__{qid}"
                answer = request.form.get(field_name, "").strip()
                role_questions.append(
                    {
                        "question_id": qid,
                        "question_text": q["text"],
                        "priority": q.get("priority", 1),
                        "answer": answer,
                    }
                )
            answers_data["answers"][rid] = {
                "role_label": role_label,
                "purpose": purpose,
                "questions": role_questions,
            }

        # Global answers
        for gq in team_data.get("global_questions", []):
            qid = gq["id"]
            field_name = f"global__{qid}"
            answer = request.form.get(field_name, "").strip()
            answers_data["global"].append(
                {
                    "question_id": qid,
                    "question_text": gq["text"],
                    "priority": gq.get("priority", 1),
                    "answer": answer,
                }
            )

        ANSWERS_FILE.write_text(json.dumps(answers_data, indent=2), encoding="utf-8")
        flash(f"Saved answers to {ANSWERS_FILE.name}", "success")
        return redirect(url_for("qna_form"))

    # GET
    answers_data = load_existing_answers(team_data)
    return render_template("qna_form.html", team=team_data, answers=answers_data)


if __name__ == "__main__":
    # Dev server
    app.run(debug=True)
