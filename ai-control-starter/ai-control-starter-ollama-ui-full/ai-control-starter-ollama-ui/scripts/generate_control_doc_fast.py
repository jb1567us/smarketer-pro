import json
import argparse
from pathlib import Path
from datetime import datetime

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

def main():
    ap = argparse.ArgumentParser(
        description="Generate control.md quickly from templates (no AI calls)."
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

    print("🚀 Generating control.md from template (instant)...")
    
    try:
        control_doc = generate_control_from_template(idea_text, team_data, answers_data)
    except Exception as e:
        raise SystemExit(f"Error generating control.md: {e}")

    out_path = Path(args.out)
    out_path.write_text(control_doc, encoding="utf-8")
    print(f"✅ Wrote Control Doc to: {out_path}")
    print(f"📄 Document size: {len(control_doc)} characters")

if __name__ == "__main__":
    main()