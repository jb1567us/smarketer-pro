import json
import sys
import argparse
from pathlib import Path

# Add the parent directory to Python path so we can import model_client
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    import model_client
    from model_client import ModelClientError
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

from flask import Flask, render_template, request, redirect, url_for, flash

ARTIFACTS_DIR = BASE_DIR / "artifacts"

IDEA_FILE = BASE_DIR / "idea.txt"
TEAM_FILE = ARTIFACTS_DIR / "team_and_questions_v0.1.json"
ANSWERS_FILE = ARTIFACTS_DIR / "intake_answers_v0.1.json"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = "replace-this-secret-key"


def create_fallback_structure(idea_text: str) -> dict:
    """Create a fallback project structure when AI generation fails"""
    return {
        "project_title": idea_text[:50] + ("..." if len(idea_text) > 50 else ""),
        "summary": f"Project based on: {idea_text[:100]}",
        "roles": [
            {
                "id": "product_manager",
                "label": "Product Manager",
                "purpose": "Define product requirements and user experience",
                "questions": [
                    {"id": "main_goal", "text": "What is the main goal of this project?", "priority": 1},
                    {"id": "target_users", "text": "Who are the target users?", "priority": 1},
                    {"id": "key_features", "text": "What are the most important features?", "priority": 2}
                ]
            },
            {
                "id": "technical_lead", 
                "label": "Technical Lead",
                "purpose": "Design the technical architecture and implementation",
                "questions": [
                    {"id": "tech_stack", "text": "What technologies should we use?", "priority": 1},
                    {"id": "scalability", "text": "Do we need to consider scalability?", "priority": 2}
                ]
            }
        ],
        "global_questions": [
            {"id": "timeline", "text": "What is the expected timeline?", "priority": 1},
            {"id": "budget", "text": "What is the budget for this project?", "priority": 2}
        ]
    }


def generate_team_and_questions(idea_text: str) -> dict:
    """Generate team structure with robust JSON parsing"""
    system_prompt = (
        "You are a project architect. Return ONLY valid JSON, no other text.\n"
        "Format:\n"
        "{\n"
        '  \"project_title\": \"string\",\n'
        '  \"summary\": \"string\",\n'
        '  \"roles\": [\n'
        '    {\"id\": \"snake_case\", \"label\": \"string\", \"purpose\": \"string\", \"questions\": [{\"id\": \"string\", \"text\": \"string\", \"priority\": 1}]}\n'
        '  ],\n'
        '  \"global_questions\": [{\"id\": \"string\", \"text\": \"string\", \"priority\": 1}]\n'
        '}'
    )

    user_prompt = f"Create project structure for: {idea_text}"

    try:
        content = model_client.generate_text(
            system_prompt, 
            user_prompt, 
            model="phi3:mini"
        ).strip()
        
        print(f"DEBUG: Raw AI response length: {len(content)}")
        
        # Clean the response - remove markdown code blocks
        cleaned_content = content.strip()
        
        # Remove ```json and ``` markers
        if cleaned_content.startswith("```"):
            # Split into lines and remove the first line if it's a code block marker
            lines = cleaned_content.split('\n')
            if lines and (lines[0].strip() == "```" or lines[0].strip().startswith("```json")):
                lines = lines[1:]
            # Remove the last line if it's a code block marker  
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_content = '\n'.join(lines).strip()
        
        print(f"DEBUG: Cleaned content length: {len(cleaned_content)}")
        
        # Parse JSON
        try:
            data = json.loads(cleaned_content)
            print("DEBUG: JSON parsing successful!")
            return data
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parse failed: {e}")
            print(f"DEBUG: First 500 chars of cleaned content: {cleaned_content[:500]}")
            
            # Try to extract JSON using regex as fallback
            import re
            json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    print("DEBUG: Successfully extracted JSON using regex")
                    return data
                except json.JSONDecodeError as e2:
                    print(f"DEBUG: Regex extraction also failed: {e2}")
            
            # If all else fails, return a default structure
            raise ValueError(f"AI did not return valid JSON: {e}")
            
    except (ModelClientError, ValueError) as e:
        print(f"DEBUG: Generation failed, using fallback: {e}")
        # Return a simple fallback structure
        return create_fallback_structure(idea_text)


def load_team():
    if not TEAM_FILE.exists():
        raise FileNotFoundError("Team file does not exist. Submit an idea first.")
    return json.loads(TEAM_FILE.read_text(encoding="utf-8"))


def load_existing_answers(team):
    if ANSWERS_FILE.exists():
        data = json.loads(ANSWERS_FILE.read_text(encoding="utf-8"))
    else:
        data = {
            "project_title": team.get("project_title", ""),
            "summary": team.get("summary", ""),
            "answers": {},
            "global": [],
        }

    data.setdefault("answers", {})

    for role in team.get("roles", []):
        rid = role["id"]
        if rid not in data["answers"]:
            data["answers"][rid] = {
                "role_label": role["label"],
                "purpose": role["purpose"],
                "questions": [],
            }

        existing_by_id = {
            q["question_id"]: q
            for q in data["answers"][rid].get("questions", [])
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
        data["answers"][rid]["questions"] = merged_questions

    existing_global = {g["question_id"]: g for g in data.get("global", [])}
    merged_global = []
    for gq in team.get("global_questions", []):
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
    data["global"] = merged_global

    return data


@app.route("/", methods=["GET", "POST"])
def idea_form():
    existing_idea = ""
    if IDEA_FILE.exists():
        existing_idea = IDEA_FILE.read_text(encoding="utf-8")

    if request.method == "POST":
        idea_text = request.form.get("idea_text", "").strip()
        if not idea_text:
            flash("Please enter your idea.", "error")
            return render_template("idea_form.html", idea_text=existing_idea)

        IDEA_FILE.write_text(idea_text, encoding="utf-8")

        try:
            flash("Generating team and questions... This may take 1-2 minutes.", "info")
            team_data = generate_team_and_questions(idea_text)
            
            # Validate the structure has required fields
            if not team_data.get("roles") or not team_data.get("project_title"):
                flash("AI response was incomplete, using enhanced fallback structure", "warning")
                team_data = create_fallback_structure(idea_text)
                
        except (ModelClientError, Exception) as e:
            flash(f"Error generating team/questions: {e}. Using fallback structure.", "error")
            team_data = create_fallback_structure(idea_text)

        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        TEAM_FILE.write_text(json.dumps(team_data, indent=2), encoding="utf-8")

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
                "questions": [
                    {
                        "question_id": q["id"],
                        "question_text": q["text"],
                        "priority": q.get("priority", 1),
                        "answer": "",
                    }
                    for q in role.get("questions", [])
                ],
            }
            
        for gq in team_data.get("global_questions", []):
            answers["global"].append(
                {
                    "question_id": gq["id"],
                    "question_text": gq["text"],
                    "priority": gq.get("priority", 1),
                    "answer": "",
                }
            )

        ANSWERS_FILE.write_text(json.dumps(answers, indent=2), encoding="utf-8")

        flash("Created team and questions from your idea. Now answer them.", "success")
        return redirect(url_for("qna_form"))

    return render_template("idea_form.html", idea_text=existing_idea)


@app.route("/questions", methods=["GET", "POST"])
def qna_form():
    try:
        team_data = load_team()
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for("idea_form"))

    if request.method == "POST":
        answers_data = {
            "project_title": team_data.get("project_title", ""),
            "summary": team_data.get("summary", ""),
            "answers": {},
            "global": [],
        }

        for role in team_data.get("roles", []):
            rid = role["id"]
            qq = []
            for q in role.get("questions", []):
                qid = q["id"]
                field_name = f"{rid}__{qid}"
                answer = request.form.get(field_name, "").strip()
                qq.append(
                    {
                        "question_id": qid,
                        "question_text": q["text"],
                        "priority": q.get("priority", 1),
                        "answer": answer,
                    }
                )
            answers_data["answers"][rid] = {
                "role_label": role["label"],
                "purpose": role["purpose"],
                "questions": qq,
            }

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
        flash("Saved answers.", "success")
        return redirect(url_for("qna_form"))

    answers_data = load_existing_answers(team_data)
    return render_template("qna_form.html", team=team_data, answers=answers_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    print(f"🚀 Starting web UI on http://127.0.0.1:{args.port}")
    print("   Using optimized JSON parsing with phi3:mini")
    print("   Press CTRL+C to stop the server")
    
    # Increase timeout for long AI generation
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    app.run(debug=True, port=args.port, threaded=True)