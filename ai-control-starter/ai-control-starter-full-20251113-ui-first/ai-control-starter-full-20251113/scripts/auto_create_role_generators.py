import json
from pathlib import Path

GEN_TEMPLATE = """import os
from pathlib import Path

try:
    import openai
except ImportError:
    openai = None


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


def main():
    # Role-specific generator script
    # Role ID: {role_id}
    # Role Label: {role_label}
    # Purpose: {purpose}

    require_openai_client()
    base_dir = Path(__file__).resolve().parents[1]
    control_path = base_dir / "control.md"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not control_path.exists():
        raise FileNotFoundError("control.md not found. Generate it first.")

    control_text = control_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are the {role_label} for this project.\n"
        "Your purpose: {purpose}\n\n"
        "You will read the project's Control Doc and produce your primary artifact "
        "for this role (e.g., spec, plan, or code scaffold)."
    )

    user_prompt = f"""Here is the current Control Doc:

"""{{control_text}}"""

Now produce a single, coherent artifact for the role '{role_label}'.
- Make it directly useful with minimal filler.
- Include enough detail that other roles (and future scripts) can build on it.
- Output ONLY the artifact content (no commentary)."""

    resp = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {{"role": "system", "content": system_prompt}},
            {{"role": "user", "content": user_prompt}},
        ],
        temperature=0.3,
    )

    content = resp["choices"][0]["message"]["content"]
    out_file = artifacts_dir / "{role_id}_artifact_v0.1.md"
    out_file.write_text(content, encoding="utf-8")

    print(f"Wrote artifact for role '{role_label}' to: {{out_file}}")


if __name__ == "__main__":
    main()
"""


def main():
    base_dir = Path(__file__).resolve().parents[1]
    artifacts_dir = base_dir / "artifacts"
    team_file = artifacts_dir / "team_and_questions_v0.1.json"

    if not team_file.exists():
        raise FileNotFoundError(
            f"{team_file} not found. Run idea/bootstrap step first."
        )

    team_data = json.loads(team_file.read_text(encoding="utf-8"))
    roles = team_data.get("roles", [])

    if not roles:
        print("No roles found in team_and_questions_v0.1.json")
        return

    gen_dir = base_dir / "scripts"
    gen_dir.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []

    for role in roles:
        role_id = role.get("id", "unnamed_role")
        role_label = role.get("label", role_id)
        purpose = (role.get("purpose", "") or "").replace('"', "'")

        script_name = f"gen_{role_id}.py"
        script_path = gen_dir / script_name

        if script_path.exists():
            skipped.append(script_name)
            continue

        script_code = GEN_TEMPLATE.format(
            role_id=role_id,
            role_label=role_label,
            purpose=purpose,
        )
        script_path.write_text(script_code, encoding="utf-8")
        created.append(script_name)

    if created:
        print("Created generator scripts:")
        for s in created:
            print("  -", s)
    else:
        print("No new generator scripts created.")

    if skipped:
        print("\nSkipped existing scripts:")
        for s in skipped:
            print("  -", s)


if __name__ == "__main__":
    main()
