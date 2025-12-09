import json
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

GEN_TEMPLATE = '''import json
import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    import model_client
    from model_client import ModelClientError
except ImportError as e:
    print(f"Import error: {{e}}")
    sys.exit(1)


def main():
    # Role-specific generator script.
    # Role ID: {role_id}
    # Role Label: {role_label}
    # Purpose: {purpose}

    base_dir = Path(__file__).resolve().parents[1]
    control_path = base_dir / "control.md"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not control_path.exists():
        raise FileNotFoundError("control.md not found. Generate it first (option 3 in run.bat).")

    control_text = control_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are the {role_label} for this project. "
        "Your purpose: {purpose}"
    )

    user_prompt = (
        "Here is the current Control Doc:\\n\\n"
        + control_text
        + "\\n\\n"
        "Produce a single, coherent artifact for the role '{role_label}'. "
        "Make it directly useful with minimal filler. "
        "Output ONLY the artifact content (no commentary)."
    )

    try:
        content = model_client.generate_text(system_prompt, user_prompt, task="coding")
    except ModelClientError as e:
        raise SystemExit(f"Error generating artifact for {role_label}: {{e}}")

    out_file = artifacts_dir / "{role_id}_artifact_v0.1.md"
    out_file.write_text(content, encoding="utf-8")
    print("Wrote artifact for role '{role_label}' to:", out_file)


if __name__ == "__main__":
    main()
'''


def main():
    base_dir = Path(__file__).resolve().parents[1]
    artifacts_dir = base_dir / "artifacts"
    team_file = artifacts_dir / "team_and_questions_v0.1.json"

    if not team_file.exists():
        raise FileNotFoundError(
            f"{team_file} not found. Run the idea/web UI step first to generate it."
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
        purpose = (role.get("purpose", "") or "").replace('"', "'").replace('{', '{{').replace('}', '}}')

        script_name = f"gen_{role_id}.py"
        script_path = gen_dir / script_name

        if script_path.exists():
            skipped.append(script_name)
            continue

        try:
            script_code = GEN_TEMPLATE.format(
                role_id=role_id,
                role_label=role_label,
                purpose=purpose,
            )
            script_path.write_text(script_code, encoding="utf-8")
            created.append(script_name)
        except KeyError as e:
            print(f"Warning: Could not create {script_name} due to template error: {e}")
            continue

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