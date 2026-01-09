import json
import sys
import argparse
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    import model_client
    from model_client import ModelClientError
except ImportError as e:
    print(f"Import error: {e}")
    # Continue without model_client for fallback mode

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = "dashboard-secret-key-2024"

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

# Chat history storage
chat_history = []

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

def generate_control_from_template(idea_text: str, team_data: dict, answers_data: dict) -> str:
    """Generate control.md from templates with smart formatting - NO AI calls"""
    
    # Extract key information
    project_title = team_data.get("project_title", "Project").strip() or "New Project"
    summary = team_data.get("summary", "").strip() or f"Project based on: {idea_text[:100]}..."
    
    # Build roles section
    roles_section = ""
    for role in team_data.get("roles", []):
        role_label = role.get("label", "Unnamed Role")
        role_purpose = role.get("purpose", "").strip() or "Role responsibilities to be defined"
        roles_section += f"### {role_label}\n"
        roles_section += f"**Purpose**: {role_purpose}\n\n"
        
        # Add questions and answers for this role
        role_id = role.get("id", "")
        role_answers = answers_data.get("answers", {}).get(role_id, {})
        for q in role_answers.get("questions", []):
            if q.get('answer', '').strip():
                roles_section += f"- **{q.get('question_text', 'Question')}**: {q.get('answer', '')}\n"
        roles_section += "\n"
    
    # Build global questions section
    global_answers = ""
    for gq in answers_data.get("global", []):
        if gq.get('answer', '').strip():
            global_answers += f"- **{gq.get('question_text', 'Question')}**: {gq.get('answer', '')}\n"
    
    # Get current date for the document
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create the control document
    control_doc = f"""# Project Control Document: {project_title}

*Generated on {current_date}*

## Executive Summary
{summary}

## Project Idea
{idea_text.strip()}

## Objectives
- Deliver a functional product that addresses the core idea
- Establish clear project boundaries and success criteria
- Create maintainable and scalable architecture
- Ensure positive user experience

## Scope & Boundaries

### In Scope
- Core functionality based on the project idea
- Essential user interface and experience
- Basic data management and storage
- Fundamental security and performance requirements

### Out of Scope (Initial Release)
- Advanced enterprise features
- Complex third-party integrations
- Mobile applications (unless specified)
- Advanced analytics and reporting

## Roles & Responsibilities

{roles_section if roles_section.strip() else "*- Roles and responsibilities to be defined -*"}

## Key Requirements

### Functional Requirements
- Core system functionality as described in the project idea
- User authentication and authorization (if needed)
- Data persistence and management
- Basic reporting and monitoring

### Non-Functional Requirements
- Responsive and intuitive user interface
- Secure data handling
- Reasonable performance under expected load
- Maintainable codebase

## Deliverables

### Phase 1: Foundation
- D1.1: Project specification and architecture design
- D1.2: Core system infrastructure
- D1.3: Basic user interface framework

### Phase 2: Core Features  
- D2.1: Main functionality implementation
- D2.2: Data management system
- D2.3: User interface completion

### Phase 3: Polish & Deployment
- D3.1: Testing and quality assurance
- D3.2: Documentation and user guides
- D3.3: Deployment and launch preparation

## Implementation Plan

### Phase 1: Setup & Design (Week 1-2)
1. **T1.1**: Define technical architecture and stack
2. **T1.2**: Set up development environment
3. **T1.3**: Create project structure and repositories
4. **T1.4**: Design database schema and APIs

### Phase 2: Core Development (Week 3-6)  
5. **T2.1**: Implement backend services
6. **T2.2**: Develop frontend components
7. **T2.3**: Create data models and business logic
8. **T2.4**: Implement user authentication (if needed)

### Phase 3: Integration & Testing (Week 7-8)
9. **T3.1**: Integrate frontend and backend
10. **T3.2**: Conduct system testing
11. **T3.3**: Performance and security testing

### Phase 4: Deployment (Week 9-10)
12. **T4.1**: Prepare deployment infrastructure
13. **T4.2**: Deploy to staging environment
14. **T4.3**: Final testing and production deployment

## Technical Constraints
- Use modern, maintainable technology stack
- Follow security best practices
- Ensure code quality through testing and reviews
- Maintain documentation throughout development

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| {current_date} | Use template-based control document | Faster generation without AI delays |
| {current_date} | Phased delivery approach | Manageable development with clear milestones |

## Open Questions & Notes

### Global Questions & Answers
{global_answers if global_answers.strip() else "*- No global questions answered yet -*"}

### Additional Considerations
- Timeline and resource allocation to be finalized
- Specific technology choices to be determined
- User testing and feedback mechanisms to be established

---
*This document will evolve as the project progresses. Regular updates are expected during development.*
"""
    
    return control_doc

@app.route("/")
def dashboard():
    """Main dashboard showing all project artifacts and status"""
    project_exists = IDEA_FILE.exists()
    team_exists = TEAM_FILE.exists()
    answers_exist = ANSWERS_FILE.exists()
    control_exists = CONTROL_FILE.exists()
    
    # Get project info
    project_info = {}
    if project_exists:
        project_info['idea'] = IDEA_FILE.read_text(encoding="utf-8")[:200] + "..." if len(IDEA_FILE.read_text(encoding="utf-8")) > 200 else IDEA_FILE.read_text(encoding="utf-8")
    
    if team_exists:
        team_data = json.loads(TEAM_FILE.read_text(encoding="utf-8"))
        project_info['title'] = team_data.get('project_title', 'Untitled')
        project_info['summary'] = team_data.get('summary', '')
        project_info['roles_count'] = len(team_data.get('roles', []))
    
    # Check for role artifacts
    role_artifacts = []
    if ARTIFACTS_DIR.exists():
        for artifact_file in ARTIFACTS_DIR.glob("*_artifact_*.md"):
            role_artifacts.append(artifact_file.name)
    
    return render_template("dashboard.html", 
                         project_exists=project_exists,
                         team_exists=team_exists,
                         answers_exist=answers_exist,
                         control_exists=control_exists,
                         project_info=project_info,
                         role_artifacts=role_artifacts)

@app.route("/generate_team", methods=["POST"])
def generate_team():
    """Generate team and questions from idea using template - no AI"""
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
    flash("Team structure created! Now answer the questions.", "success")
    return redirect(url_for("dashboard"))

@app.route("/generate_control", methods=["POST"])
def generate_control():
    """Generate control document"""
    if not all([IDEA_FILE.exists(), TEAM_FILE.exists(), ANSWERS_FILE.exists()]):
        flash("Need idea, team, and answers to generate control document.", "error")
        return redirect(url_for("dashboard"))
    
    try:
        idea_text = IDEA_FILE.read_text(encoding="utf-8")
        team_data = json.loads(TEAM_FILE.read_text(encoding="utf-8"))
        answers_data = json.loads(ANSWERS_FILE.read_text(encoding="utf-8"))
        
        control_doc = generate_control_from_template(idea_text, team_data, answers_data)
        CONTROL_FILE.write_text(control_doc, encoding="utf-8")
        flash("Control document generated successfully!", "success")
    except Exception as e:
        flash(f"Error generating control document: {e}", "error")
    
    return redirect(url_for("dashboard"))

@app.route("/generate_role_artifacts", methods=["POST"])
def generate_role_artifacts():
    """Generate all role artifacts"""
    if not CONTROL_FILE.exists():
        flash("Generate control document first.", "error")
        return redirect(url_for("dashboard"))
    
    try:
        # Import and run the fast generators
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        from gen_product_manager_fast import main as gen_pm
        from gen_technical_lead_fast import main as gen_tl
        
        gen_pm()
        gen_tl()
        
        flash("Role artifacts generated successfully!", "success")
    except Exception as e:
        flash(f"Error generating role artifacts: {e}", "error")
    
    return redirect(url_for("dashboard"))

@app.route("/view_artifact/<artifact_type>")
def view_artifact(artifact_type):
    """View specific artifacts"""
    if artifact_type == "control" and CONTROL_FILE.exists():
        content = CONTROL_FILE.read_text(encoding="utf-8")
        return render_template("view_artifact.html", 
                             title="Control Document",
                             content=content,
                             artifact_type="control")
    
    elif artifact_type == "idea" and IDEA_FILE.exists():
        content = IDEA_FILE.read_text(encoding="utf-8")
        return render_template("view_artifact.html",
                             title="Project Idea",
                             content=content,
                             artifact_type="idea")
    
    elif artifact_type.startswith("role_"):
        role_name = artifact_type.replace("role_", "")
        artifact_file = ARTIFACTS_DIR / f"{role_name}_artifact_v0.1.md"
        if artifact_file.exists():
            content = artifact_file.read_text(encoding="utf-8")
            return render_template("view_artifact.html",
                                 title=f"{role_name.replace('_', ' ').title()} Artifact",
                                 content=content,
                                 artifact_type=artifact_type)
    
    flash("Artifact not found.", "error")
    return redirect(url_for("dashboard"))

# Integrated Questions Functionality
@app.route("/integrated_questions")
def integrated_questions():
    """Integrated questions page within the dashboard"""
    try:
        team_data = load_team()
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for("dashboard"))

    answers_data = load_existing_answers(team_data)
    return render_template("qna_form.html", team=team_data, answers=answers_data)

@app.route("/save_answers", methods=["POST"])
def save_answers():
    """Save answers from the integrated questions form"""
    try:
        team_data = load_team()
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for("dashboard"))

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
    flash("Answers saved successfully!", "success")
    return redirect(url_for("dashboard"))

# Enhanced AI-powered chat with proper error handling
@app.route("/chat", methods=["GET", "POST"])
def chat():
    """Interactive AI-powered chat for real plan refinement"""
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        if not user_message:
            flash("Please enter a message.", "error")
            return redirect(url_for("chat"))
        
        # Add user message to history
        chat_history.append({"role": "user", "content": user_message})
        
        try:
            # Try to use AI with proper error handling
            try:
                # Build context from current project
                context = ""
                project_title = "your project"
                if CONTROL_FILE.exists():
                    control_content = CONTROL_FILE.read_text(encoding="utf-8")
                    context = f"\n\nCurrent Project Context:\n{control_content[:1000]}..."
                    
                    # Extract project title for personalization
                    if "# Project Control Document:" in control_content:
                        title_line = [line for line in control_content.split('\n') if "# Project Control Document:" in line][0]
                        project_title = title_line.replace("# Project Control Document:", "").strip()

                system_prompt = """You are an expert project planning assistant. The user is working on a REAL project and needs SPECIFIC, actionable advice tailored to their actual project context.

IMPORTANT: 
- Reference their actual project details from the context
- Provide concrete, specific suggestions they can implement
- Focus on practical improvements, not generic advice
- Be concise but thorough
- Suggest actual changes to their plan
- If they mention specific features, timeline, or budget, address those directly"""

                user_prompt = f"""User question: {user_message}

{context}

Please provide SPECIFIC, actionable advice for this actual project. Reference their actual goals, timeline, and constraints from the context above."""

                # Use faster model with shorter timeout
                ai_response = model_client.generate_text_fast(
                    system_prompt,
                    user_prompt,
                    model="phi3:mini",  # Much faster than llama3
                    timeout=90  # Shorter timeout for chat
                )
                
                chat_history.append({"role": "assistant", "content": ai_response})
                flash("✅ AI analysis complete! This is tailored to YOUR project.", "success")
                
            except (ImportError, ModelClientError, Exception) as ai_error:
                # If AI fails, provide helpful fallback
                flash("⚠️ AI temporarily unavailable. Using enhanced templates with your project context.", "info")
                
                # Enhanced template responses that reference actual project
                project_context = ""
                if CONTROL_FILE.exists():
                    control_content = CONTROL_FILE.read_text(encoding="utf-8")
                    # Extract project title for personalization
                    if "# Project Control Document:" in control_content:
                        title_line = [line for line in control_content.split('\n') if "# Project Control Document:" in line][0]
                        project_title = title_line.replace("# Project Control Document:", "").strip()
                        project_context = f" for '{project_title}'"
                
                user_lower = user_message.lower()
                
                if any(word in user_lower for word in ["timeline", "schedule", "deadline"]):
                    ai_response = f"""## Timeline Analysis{project_context}

Based on your current project setup, here's how to optimize your timeline:

### Current State Analysis:
Your project appears to be in the planning phase. The standard timeline can likely be accelerated.

### Recommended Accelerated Timeline:

**Weeks 1-2: Rapid Foundation**
- Set up core infrastructure and basic components
- Implement essential backend functionality
- Create basic UI and user flows

**Weeks 3-4: Core Features**
- Focus on your key differentiators
- Implement primary user workflows
- Build essential integrations

**Weeks 5-6: Launch Preparation**
- Testing with real users
- Refine based on early feedback
- Prepare deployment and marketing

### Key Acceleration Opportunities:
1. **Use existing templates and components** where possible
2. **Focus on core value proposition** first
3. **Implement basic version**, enhance based on user feedback
4. **Leverage existing tools and services** to speed development

Would you like me to help you adjust specific timeline milestones?"""

                elif any(word in user_lower for word in ["budget", "cost", "$0"]):
                    ai_response = f"""## Budget Optimization{project_context}

Given your budget constraints, here's a sustainable approach:

### Immediate Cost-Free Infrastructure:
- **Frontend**: Vercel (free) - excellent for modern web apps
- **Backend**: Railway/Render (free) - reliable hosting options
- **Database**: Supabase (free) - includes auth and realtime
- **CDN**: Cloudflare (free) - performance and security

### Smart Cost Management:
1. **Start with free tiers** - upgrade only when necessary
2. **Use serverless architecture** - pay only for what you use
3. **Optimize assets** - reduce bandwidth costs
4. **Monitor usage** - avoid surprise costs

### Revenue-First Approach:
- Launch with core features that provide immediate value
- Focus on user acquisition and retention
- Use early revenue to fund platform improvements
- Consider freemium or tiered pricing models

### Phase-Based Financial Plan:
- **Launch**: Minimal costs using free tiers
- **Growth**: Scale costs with user growth
- **Scale**: Optimize infrastructure as revenue increases"""

                elif any(word in user_lower for word in ["feature", "priority", "mvp"]):
                    ai_response = f"""## Feature Prioritization{project_context}

For optimal launch success, here's the recommended feature sequence:

### MVP (Launch Ready):
1. **Core Value Proposition**
   - The main problem your project solves
   - Essential user workflows
   - Basic user interface

2. **Essential Functionality**
   - Key features that deliver value
   - Basic user management
   - Core data operations

3. **Minimum Viable Experience**
   - Smooth user onboarding
   - Clear value demonstration
   - Basic help/support

### Phase 2 (Post-Launch):
4. **Enhanced User Experience**
   - Improved workflows
   - Additional features based on feedback
   - Performance optimizations

5. **Advanced Features**
   - Power user tools
   - Integration capabilities
   - Advanced analytics

### Critical Success Factors:
- **Focus on core value** - what makes your project unique
- **Solve the main pain point** - address primary user needs
- **Keep it simple** - avoid feature bloat
- **Iterate based on feedback** - build what users actually want"""

                else:
                    ai_response = f"""## Project Guidance{project_context}

I can see you're working on an interesting project. Let me provide specific guidance:

### Based on Your Project Context:
You're building something with clear goals and target audience. This is a great starting point.

### Immediate Next Steps:
1. **Validate your core assumptions** with potential users
2. **Set up your development environment** with the right tools
3. **Focus on your MVP** - the minimum set of features that delivers value
4. **Create your launch plan** - how you'll reach your first users

### Key Opportunities:
- **Leverage your unique insights** about the problem space
- **Focus on user experience** from day one
- **Build a feedback loop** with early users
- **Iterate quickly** based on real usage

What specific challenge would you like to tackle first?"""

                chat_history.append({"role": "assistant", "content": ai_response})
                
        except Exception as e:
            # Ultimate fallback
            error_response = "I'd love to help you refine your specific project! Could you tell me more about what particular aspect you'd like to improve? For example: timeline optimization, feature prioritization, technical architecture, or go-to-market strategy?"
            chat_history.append({"role": "assistant", "content": error_response})
            flash("Please try asking a more specific question about your project.", "info")
        
        return redirect(url_for("chat"))
    
    return render_template("chat.html", chat_history=chat_history)

@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    """Clear chat history"""
    global chat_history
    chat_history = []
    flash("Chat history cleared.", "success")
    return redirect(url_for("chat"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    print(f"🚀 Starting Unified Dashboard on http://127.0.0.1:{args.port}")
    print("   All features accessible from single interface!")
    print("   AI-powered chat with real project analysis!")
    print("   Press CTRL+C to stop the server")
    
    app.run(debug=True, port=args.port)