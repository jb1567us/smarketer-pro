import json
import sys
import argparse
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = "simple-dashboard-2024"

ARTIFACTS_DIR = BASE_DIR / "artifacts"
IDEA_FILE = BASE_DIR / "idea.txt"
TEAM_FILE = ARTIFACTS_DIR / "team_and_questions_v0.1.json"
ANSWERS_FILE = ARTIFACTS_DIR / "intake_answers_v0.1.json"
CONTROL_FILE = BASE_DIR / "control.md"

# Simple team structure template
DEFAULT_TEAM_STRUCTURE = {
    "project_title": "New Project",
    "summary": "A project created with AI Control Starter",
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

chat_history = []

@app.route("/")
def dashboard():
    """Main dashboard - completely AI-free"""
    project_exists = IDEA_FILE.exists()
    team_exists = TEAM_FILE.exists()
    answers_exist = ANSWERS_FILE.exists()
    control_exists = CONTROL_FILE.exists()
    
    project_info = {}
    if project_exists:
        project_info['idea'] = IDEA_FILE.read_text(encoding="utf-8")[:200] + "..." if len(IDEA_FILE.read_text(encoding="utf-8")) > 200 else IDEA_FILE.read_text(encoding="utf-8")
    
    if team_exists:
        team_data = json.loads(TEAM_FILE.read_text(encoding="utf-8"))
        project_info['title'] = team_data.get('project_title', 'Untitled')
        project_info['summary'] = team_data.get('summary', '')
        project_info['roles_count'] = len(team_data.get('roles', []))
    
    role_artifacts = []
    if ARTIFACTS_DIR.exists():
        for artifact_file in ARTIFACTS_DIR.glob("*_artifact_*.md"):
            role_artifacts.append(artifact_file.name)
    
    return render_template("dashboard_simple.html", 
                         project_exists=project_exists,
                         team_exists=team_exists,
                         answers_exist=answers_exist,
                         control_exists=control_exists,
                         project_info=project_info,
                         role_artifacts=role_artifacts)

@app.route("/generate_team", methods=["POST"])
def generate_team():
    """Generate team using template - no AI"""
    idea_text = request.form.get("idea_text", "").strip()
    if not idea_text:
        flash("Please enter your idea.", "error")
        return redirect(url_for("dashboard"))
    
    IDEA_FILE.write_text(idea_text, encoding="utf-8")
    
    # Use template structure with custom project title
    team_data = DEFAULT_TEAM_STRUCTURE.copy()
    team_data["project_title"] = idea_text[:50] + ("..." if len(idea_text) > 50 else "")
    team_data["summary"] = f"Project based on: {idea_text[:100]}..."
    
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    TEAM_FILE.write_text(json.dumps(team_data, indent=2), encoding="utf-8")
    
    # Create answers template
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
    flash("Team structure created using template! Now answer the questions.", "success")
    return redirect(url_for("dashboard"))

# ... include all the other routes from the previous dashboard but remove AI dependencies ...

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """Fast template-based chat - no AI calls"""
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        if not user_message:
            flash("Please enter a message.", "error")
            return redirect(url_for("chat"))
        
        chat_history.append({"role": "user", "content": user_message})
        
        # Template-based responses
        response_templates = {
            "timeline": "For faster development, consider a 6-week MVP timeline with simplified features.",
            "budget": "With a $0 budget, focus on free tiers: Vercel, Railway, Supabase, and Cloudflare.",
            "feature": "Prioritize: 1) Artwork catalog 2) Basic e-commerce 3) Essential pages",
            "target": "Focus on: 1) Interior designers 2) Existing followers 3) Art enthusiasts",
            "help": "I can help with: timeline, budget, features, target audience, or technical questions."
        }
        
        # Find matching template
        ai_response = response_templates["help"]  # default
        for key, response in response_templates.items():
            if key in user_message.lower():
                ai_response = response
                break
        
        chat_history.append({"role": "assistant", "content": ai_response})
        return redirect(url_for("chat"))
    
    return render_template("chat_simple.html", chat_history=chat_history)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    print(f"🚀 Starting AI-Free Dashboard on http://127.0.0.1:{args.port}")
    print("   All features work instantly without AI dependencies!")
    print("   Press CTRL+C to stop the server")
    
    app.run(debug=True, port=args.port)