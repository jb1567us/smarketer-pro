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
    ap.add_argument("--fast", action="store_true", help="Use faster model (phi3:mini)")
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

    # Create a more concise context to reduce token count
    concise_context = {
        "idea": idea_text[:500],  # Limit idea length
        "project_title": team_data.get("project_title", ""),
        "summary": team_data.get("summary", ""),
        "roles": [],
        "key_answers": {}
    }

    # Include only key role information
    for role in team_data.get("roles", [])[:5]:  # Limit to 5 roles
        concise_context["roles"].append({
            "label": role.get("label", ""),
            "purpose": role.get("purpose", "")[:200]  # Limit purpose length
        })

    # Include only non-empty answers
    for role_id, role_data in answers_data.get("answers", {}).items():
        non_empty_answers = [
            f"Q: {q.get('question_text', '')[:100]} A: {q.get('answer', '')[:200]}"
            for q in role_data.get("questions", [])
            if q.get('answer', '').strip()
        ]
        if non_empty_answers:
            concise_context["key_answers"][role_id] = non_empty_answers[:3]  # Limit to 3 answers per role

    user_prompt = (
        "Create a project control document based on this information:\n\n"
        f"Project: {concise_context['project_title']}\n"
        f"Idea: {concise_context['idea']}\n"
        f"Summary: {concise_context['summary']}\n\n"
        "Roles:\n" + "\n".join([f"- {r['label']}: {r['purpose']}" for r in concise_context['roles']]) + "\n\n"
        "Key Answers:\n" + "\n".join([
            f"- {role}: " + "; ".join(answers)
            for role, answers in concise_context['key_answers'].items()
        ]) + "\n\n"
        "Generate a comprehensive control.md with these sections:\n"
        "1. # Project Control Doc\n"
        "2. ## Objective (1-3 measurable bullets)\n" 
        "3. ## Scope & Non-Goals\n"
        "4. ## Roles & Responsibilities\n"
        "5. ## Deliverables (D1, D2, ...)\n"
        "6. ## Task Graph (T1, T2, ... with dependencies)\n"
        "7. ## Constraints\n"
        "8. ## Decision Log (seed with initial decisions)\n"
        "9. ## Open Questions\n"
        "Output ONLY valid Markdown, no commentary."
    )

    print(f"Generating control.md with {len(user_prompt)} characters...")
    
    try:
        # Use faster model if specified or by default
        model_to_use = "phi3:mini" if args.fast else None
        control_md = model_client.generate_text(
            CONTROL_DOC_SYSTEM, 
            user_prompt, 
            task="planning",
            model=model_to_use
        )
    except ModelClientError as e:
        raise SystemExit(f"Error generating control.md: {e}")

    out_path = Path(args.out)
    out_path.write_text(control_md, encoding="utf-8")
    print(f"Wrote Control Doc to: {out_path}")