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

def generate_simple_control_doc(idea_text: str, team_data: dict, answers_data: dict) -> str:
    """Generate a simpler control document that's faster to create"""
    
    # Extract key information
    project_title = team_data.get("project_title", "Untitled Project")
    summary = team_data.get("summary", "")
    
    # Get roles
    roles_section = ""
    for role in team_data.get("roles", []):
        roles_section += f"### {role.get('label', '')}\n"
        roles_section += f"**Purpose**: {role.get('purpose', '')}\n\n"
    
    # Get key answers
    answers_section = ""
    for role_id, role_data in answers_data.get("answers", {}).items():
        for q in role_data.get("questions", []):
            if q.get('answer', '').strip():
                answers_section += f"- **{q.get('question_text', '')}**: {q.get('answer', '')}\n"
    
    # Create the control document template
    control_doc = f"""# Project Control Document: {project_title}

## Objective
- Transform the idea into a working product
- Deliver value to target users
- Establish clear project boundaries

## Summary
{summary}

## Scope & Non-Goals
**In Scope:**
- Core functionality based on project idea
- Basic user interface
- Essential features

**Out of Scope:**
- Advanced enterprise features  
- Complex integrations initially
- Mobile apps (unless specified)

## Roles & Responsibilities
{roles_section}

## Key Requirements & Answers
{answers_section}

## Deliverables
- D1: Project specification and architecture
- D2: Core functionality implementation  
- D3: User interface and experience
- D4: Testing and quality assurance
- D5: Deployment and documentation

## Task Graph
1. T1: Define requirements ✓
2. T2: Design architecture → T3, T4
3. T3: Implement backend → T5
4. T4: Develop frontend → T5  
5. T5: Integration testing → T6
6. T6: Deployment preparation

## Constraints
- Timeline: To be determined
- Budget: To be specified
- Technical: Use appropriate stack for requirements

## Decision Log
1. **Architecture**: Will use modular design
2. **Technology**: Stack to be determined based on requirements
3. **Deployment**: Cloud-based solution preferred

## Open Questions
- Specific technical stack decisions
- Timeline and milestone dates
- Resource allocation and team size
"""

    return control_doc

def main():
    ap = argparse.ArgumentParser(
        description="Generate a simple control.md from idea + Q&A JSON."
    )
    ap.add_argument("--idea", required=True, help="Path to idea.txt")
    ap.add_argument("--team", default="artifacts/team_and_questions_v0.1.json",
                    help="Path to team_and_questions JSON")
    ap.add_argument("--answers", default="artifacts/intake_answers_v0.1.json",
                    help="Path to filled intake answers JSON")
    ap.add_argument("--out", default="control.md", help="Where to write the Control Doc")
    args = ap.parse_args()

    idea_path = Path(args.idea)
    team_path = Path(args.team)
    answers_path = Path(args.answers)

    if not idea_path.exists():
        raise FileNotFoundError(f"Idea file not found: {idea_path}")
    if not team_path.exists():
        raise FileNotFoundError(f"Team JSON not found: {team_path}")
    if not answers_path.exists():
        raise FileNotFoundError(f"Answers JSON not found: {answers_path}")

    idea_text = idea_path.read_text(encoding="utf-8")
    team_data = json.loads(team_path.read_text(encoding="utf-8"))
    answers_data = json.loads(answers_path.read_text(encoding="utf-8"))

    print("Generating simple control.md...")
    
    try:
        control_doc = generate_simple_control_doc(idea_text, team_data, answers_data)
    except Exception as e:
        raise SystemExit(f"Error generating control.md: {e}")

    out_path = Path(args.out)
    out_path.write_text(control_doc, encoding="utf-8")
    print(f"Wrote Simple Control Doc to: {out_path}")

if __name__ == "__main__":
    main()