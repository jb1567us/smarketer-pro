import os
import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash

# Optional import (will error if missing packages)
try:
    import openai
except ImportError:
    openai = None

BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BASE_DIR / "artifacts"

IDEA_FILE = BASE_DIR / "idea.txt"
TEAM_FILE = ARTIFACTS_DIR / "team_and_questions_v0.1.json"
ANSWERS_FILE = ARTIFACTS_DIR / "intake_answers_v0.1.json"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = "replace-this-secret"


# -------------------------
# HELPERS
# -------------------------

def require_openai():
    """Ensure OpenAI is installed and API key is set."""
    if openai is None:
        raise RuntimeError("The 'openai' package is not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    openai.api_key = api_key


def generate_team_and_questions(idea_text: str) -> dict:
    """Call OpenAI to produce team + questions from idea."""
    require_openai()

    system_prompt = (
        "You are an AI project architect.\n"
        "Given a project idea, you must:\n"
        "- Create a list of roles.\n"
        "- For each role, include 3–7 high-value questions.\n"
        "- Include 3–10 global questions.\n"
        "Return ONLY valid JSON.\n"
    )

    user_prompt = (
        "Project idea:\n"
        "----------------------\n"
        f"{idea_text}\n"
        "----------------------\n\n"
        "Return JSON in this shape:\n\n"
        "{\n"
        '  "project_title": "string",\n'
        '  "summary": "string",\n'
        '  "roles": [\n'
        "    {\n"
        '      "id": "snake_case",\n'
        '      "label": "string",\n'
        '      "purpose": "string",\n'
        '      "questions": [\n'
        "        {\"id\": \"string\", \"text\": \"string\", \"priority\": 1}\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "global_questions": [\n'
        "    {\"id\": \"string\", \"text\": \"string\", \"priority\": 1}\n"
        "  ]\n"
        "}\n"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    content = response["choices"][0]["message"]["content"].strip()

    # Strip ```json fences if present
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json", "", 1).strip()

    return json.loads(content)


def load_team():
    if not TEAM_FILE.exists():
        raise FileNotFoundError("Team file does not exist. Submit an idea first.")
    return json.loads(TEAM_FILE.read_text())


def load_existing_answers(team):
    """Load answers, or create default empty structure."""
    if ANSWERS_FILE.exists():
        data = json.loads(ANSWERS_FILE.read_text())
    else:
        data = {"project_title": team["project_title"], "summary": team["summary"], "answers": {}, "global": []}

    # Ensure structure matches team file
    for role in team["roles"]:
        rid = role["id"]
        if rid not in data["answers"]:
            data["answers"][rid] = {
                "role_label": role["label"],
                "purpose": role["purpose"],
                "questions": [],
            }

        q_map = {item["question_id"]: item for item in data["answers"][rid]["questions"]}
        merged = []
        for q in role["questions"]:
            merged.append({
                "question_id": q["id"],
                "question_text": q["text"],
                "priority": q.get("priority", 1),
                "answer": q_map.get(q["id"], {}).get("answer", "")
            })
        data["answers"][rid]["questions"] = merged

    # Global questions
    g_map = {g["question_id"]: g for g in data.get("global", [])}
    merged_gq = []
    for gq in team.get("global_questions", []):
        merged_gq.append({
            "question_id": gq["id"],
            "question_text": gq["text"],
            "priority": gq.get("priority", 1),
            "answer": g_map.get(gq["id"], {}).get("answer", "")
        })
    data["global"] = merged_gq

    return data


# -------------------------
# ROUTES
# -------------------------

@app.route("/", methods=["GET", "POST"])
def idea_form():
    """UI Step 1: Submit project idea."""
    existing = IDEA_FILE.read_text() if IDEA_FILE.exists() else ""

    if request.method == "POST":
        idea_text = request.form.get("idea_text", "").strip()
        if not idea_text:
            flash("Please enter your idea.", "error")
            return render_template("idea_form.html", idea_text=existing)

        IDEA_FILE.write_text(idea_text)

        try:
            team = generate_team_and_questions(idea_text)
        except Exception as e:
            flash(f"OpenAI error: {e}", "error")
            return render_template("idea_form.html", idea_text=idea_text)

        ARTIFACTS_DIR.mkdir(exist_ok=True)
        TEAM_FILE.write_text(json.dumps(team, indent=2))

        # Build a blank answers file
        answers = {
            "project_title": team["project_title"],
            "summary": team["summary"],
            "answers": {},
            "global": [],
        }
        for role in team["roles"]:
            answers["answers"][role["id"]] = {
                "role_label": role["label"],
                "purpose": role["purpose"],
                "questions": [{"question_id": q["id"], "question_text": q["text"], "priority": q.get("priority", 1), "answer": ""} for q in role["questions"]]
            }
        for gq in team.get("global_questions", []):
            answers["global"].append({"question_id": gq["id"], "question_text": gq["text"], "priority": gq.get("priority", 1), "answer": ""})

        ANSWERS_FILE.write_text(json.dumps(answers, indent=2))

        return redirect(url_for("qna_form"))

    return render_template("idea_form.html", idea_text=existing)


@app.route("/questions", methods=["GET", "POST"])
def qna_form():
    """UI Step 2: Answer role questions."""
    try:
        team = load_team()
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("idea_form"))

    if request.method == "POST":
        data = {
            "project_title": team["project_title"],
            "summary": team["summary"],
            "answers": {},
            "global": [],
        }

        for role in team["roles"]:
            rid = role["id"]
            questions = []
            for q in role["questions"]:
                fid = f"{rid}__{q['id']}"
                answer = request.form.get(fid, "").strip()
                questions.append({
                    "question_id": q["id"],
                    "question_text": q["text"],
                    "priority": q.get("priority", 1),
                    "answer": answer
                })
            data["answers"][rid] = {
                "role_label": role["label"],
                "purpose": role["purpose"],
                "questions": questions,
            }

        for gq in team["global_questions"]:
            fid = f"global__{gq['id']}"
            ans = request.form.get(fid, "").strip()
            data["global"].append({
                "question_id": gq["id"],
                "question_text": gq["text"],
                "priority": gq.get("priority", 1),
                "answer": ans
            })

        ANSWERS_FILE.write_text(json.dumps(data, indent=2))
        flash("Saved answers!", "success")
        return redirect(url_for("qna_form"))

    data = load_existing_answers(team)
    return render_template("qna_form.html", team=team, answers=data)


if __name__ == "__main__":
    app.run(debug=True)
